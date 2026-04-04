""" Validate workbook sheet structure for the recipe template spreadsheet.
"""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FODS_PATH = ROOT / 'recipes' / 'Ice-Cream-Recipes.fods'


def load_spreadsheet_support_class(load_script_module):
    """Load the script module and return SpreadSheetSupport."""
    module = load_script_module('recipe.py', 'recipe')
    return module.SpreadSheetSupport


def test_template_workbook_has_only_one_named_sheet(load_script_module):
    """The workbook must contain exactly one sheet: Template (Deluxe)."""
    # Arrange
    spread_sheet_support = load_spreadsheet_support_class(load_script_module)

    # Act
    table_names = spread_sheet_support.list_sheet_names(FODS_PATH)

    # Assert
    assert table_names == ['Template']


def test_list_sheet_names_rejects_unsupported_suffix(load_script_module):
    """Unsupported spreadsheet suffixes should raise a ValueError."""
    # Arrange
    spread_sheet_support = load_spreadsheet_support_class(load_script_module)
    invalid_path = ROOT / 'recipes' / 'Ice-Cream-Recipes.xlsx'

    # Act / Assert
    with pytest.raises(ValueError, match='Unsupported file type'):
        spread_sheet_support.list_sheet_names(invalid_path)
