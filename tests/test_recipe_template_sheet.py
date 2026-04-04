""" Validate workbook sheet structure for the recipe template spreadsheet.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FODS_PATH = ROOT / 'recipes' / 'Ice-Cream-Recipes.fods'


def load_spreadsheet_support_class(load_script_module):
    """Load the script module and return SpreadSheetSupport."""
    module = load_script_module('recipe.py', 'recipe')
    return module.SpreadSheetSupport


def test_template_workbook_has_only_one_named_sheet(load_script_module):
    """The workbook must contain exactly one sheet: Template (Deluxe)."""
    spread_sheet_support = load_spreadsheet_support_class(load_script_module)
    table_names = spread_sheet_support.list_sheet_names(FODS_PATH)
    assert table_names == ['Template']
