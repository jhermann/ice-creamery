""" Pytest coverage for metric-to-imperial kitchen unit formatting.
"""

import re
import importlib.util

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / 'scripts' / 'ice-cream-recipe.py'
README_PATH = ROOT / 'recipes'
README_CASE_RX = re.compile(r'-\s+_([0-9]+(?:\.[0-9]+)?)([a-zA-Z ]*)_.*?\(≈([^\)]+)\)')


def load_transform_class():
    """Load the script module and return ImperialUnitTransform."""
    spec = importlib.util.spec_from_file_location('ice_cream_recipe', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.ImperialUnitTransform


def extract_readme_cases():
    """Extract all '(≈...)' conversions from recipe README files."""
    observed = {}
    for readme in README_PATH.rglob('README.md'):
        text = readme.read_text(encoding='utf-8')
        for line in text.splitlines():
            match = README_CASE_RX.search(line)
            if not match:
                continue
            amount = match.group(1)
            unit = match.group(2).strip().lower()
            imperial = match.group(3).strip()
            if unit in {'g', 'ml'}:
                observed.setdefault((amount, unit), imperial)
    return observed


ESSENTIAL_CASES = [
    ('1', 'g', '¼ tsp'),
    ('2', 'g', '½ tsp'),
    ('15', 'g', '1 tbsp'),
    ('21', 'g', '1 tbsp + 1 ¼ tsp'),
    ('35', 'g', '1 oz + 1 ¼ tsp'),
    ('100', 'g', '3 oz + 1 tbsp'),
    ('225', 'g', '7 oz + 1 tbsp + 2 ½ tsp'),
    ('30', 'ml', '2 tbsp'),
    ('100', 'ml', '3 fl oz + 2 ¼ tsp'),
    ('120', 'ml', '4 fl oz'),
    ('350', 'ml', '1 cup + 3 fl oz + 1 tbsp'),
    ('575', 'ml', '2 cups + 3 fl oz'),
]


@pytest.fixture(scope='module')
def transform():
    """Provide loaded ImperialUnitTransform class."""
    return load_transform_class()


def test_readme_extraction_contains_essential_cases():
    """Ensure each essential case comes from real generated README content."""
    readme_cases = extract_readme_cases()
    missing = [
        f'{amount}{unit} -> {expected}'
        for amount, unit, expected in ESSENTIAL_CASES
        if readme_cases.get((amount, unit)) != expected
    ]
    assert missing == []


@pytest.mark.parametrize('amount, unit, expected', ESSENTIAL_CASES)
def test_volume_combo_for_essential_cases(transform, amount, unit, expected):
    """Verify a reduced matrix that covers all major output patterns."""
    assert transform.volume_combo(amount, unit) == expected


@pytest.mark.parametrize(
    'amount, unit',
    [
        ('10', 'kg'),
        ('abc', 'g'),
        ('0', 'ml'),
        ('-1', 'g'),
    ],
)
def test_volume_combo_guard_rails(transform, amount, unit):
    """Unsupported unit, bad number, and non-positive values return empty."""
    assert transform.volume_combo(amount, unit) == ''
