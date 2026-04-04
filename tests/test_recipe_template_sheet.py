""" Validate workbook sheet structure for the recipe template spreadsheet.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
FODS_PATH = ROOT / 'recipes' / 'Ice-Cream-Recipes.fods'
TABLE_NAMESPACE = {'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}


def test_template_workbook_has_only_one_named_sheet():
    """The workbook must contain exactly one sheet: Template (Deluxe)."""
    root = ET.parse(FODS_PATH).getroot()
    tables = root.findall('.//table:table', TABLE_NAMESPACE)
    table_names = [table.attrib.get(f"{{{TABLE_NAMESPACE['table']}}}name") for table in tables]

    assert table_names == ['Template']
