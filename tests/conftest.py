"""Shared test helpers for loading script modules from the scripts folder.
"""

import sys
import importlib.util

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PATH = ROOT / 'scripts'


@pytest.fixture(scope='module')
def load_script_module():
    """Provide a helper for loading modules from the scripts directory."""

    def _load(script_name: str, module_name: str):
        if str(SCRIPTS_PATH) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_PATH))

        script_path = SCRIPTS_PATH / script_name
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module

    return _load
