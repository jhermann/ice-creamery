#! /usr/bin/env python3
"""
    Python script that provides some helpers for the icecreamcalc webapp.

    Links:
        - https://icecreamcalc.com/
        - https://www.icecreamcalc.app/

    Copyright (c) 2025 Jürgen Hermann

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import os
import re
import csv
import sys
import json
import argparse
import importlib.util as imp_util

from pprint import pp  # pylint: disable=unused-import
from pathlib import Path
from operator import itemgetter
from collections import defaultdict

import sys

def load_module(file_name, module_name=''):
    """Load a script fiel as a module."""
    module_name = module_name or Path(file_name).stem.replace('-', '_')
    spec = imp_util.spec_from_file_location(module_name, file_name)
    module = imp_util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

recipe_lib = load_module(Path(__file__).parent / 'ice-cream-recipe.py')
#pp(dir(recipe_lib))

CSV_FILE = 'Ice-Cream-Recipes.csv'
RECIPE_BODY = """{{
  "formatVersion": "1.0",
  "exportDate": "2025-10-01T00:00:00",
  "recipes": [
    {{
      "name": "{title}",
      "info": "TODO",
      "evaporation": 0,
      "created": "2025-10-11T13:24:01.1941971",
      "changed": "2025-10-11T13:24:18.7948975",
      "chartName": null,
      "ingredients": [{items}],
      "canImport": true,
      "matchedIngredientsCount": 0,
      "hasNameConflict": false,
      "importStatus": "\u2705 Ready to import",
      "importName": "{title}"
    }}
  ]
}}"""
RECIPE_ITEM = """{{
    "name": "{name}",
    "weight": {amount},
    "inclusion": false,
    "infusion": false,
    "ingredientId": null,
    "isMatched": false,
    "isAddIn": false,
    "ingredientType": "Base"
}}"""
INGREDIENTS_BODY = """{{
  "exportVersion": "1.0",
  "exportDate": "2025-10-01T00:00:00.0000000Z",
  "exportedBy": "jh@web.de",
  "ingredients": [{items}]
}}"""
INGREDIENTS_ITEM = """{{
    "name": "{name}",
    "category": "",
    "info": "{comment}",
    "created": "2025-10-01T00:00:00.0000000Z",
    "changed": "2025-10-01T00:00:00.0000000Z",
    "water": 0.0,
    "totalFat": {fat},
    "saturatedFat": 0,
    "transFat": 0,
    "cocoaFat": 0,
    "milkFat": 0,
    "cholesterol": 0,
    "sodium": 0,
    "salt": {salt},
    "alcohol": 0,
    "carbohydrates": 0.764,
    "fiber": 0.002,
    "totalSugars": 0.68,
    "addedSugars": 0,
    "polyols": 0,
    "lactose": 0,
    "protein": 0.0009,
    "vitaminD": 0,
    "calcium": 1E-05,
    "iron": 0,
    "potassium": 0,
    "otherSolids": 0,
    "cocoaSolids": 0,
    "totalSolids": 0,
    "msnf": 0,
    "stabilizers": 0,
    "emulsifiers": 0,
    "pac": 1.0,
    "pod": 1.0,
    "hf": 0,
    "costKg": 0,
    "amountMin": 0,
    "amountMax": 1,
    "containsAllergens": [],
    "mayContainAllergens": [],
    "gramPermL": 1,
    "nutrientsVerified": false,
    "portionSize": 100
}}"""

def parse_cli(argv=None):
    """"""
    argv = argv or sys.argv
    parser = argparse.ArgumentParser(
        prog='icc-tool',
        description=__doc__.split('.', 1)[0].strip() + '.',
        epilog='See https://github.com/jhermann/ice-creamery/#readme for more.')

    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Do not write results to file system.')
    parser.add_argument('-I', '--as-ingredients', action='store_true',
                        help='Transform the CSV to an ingredients import.')
    parser.add_argument('-R', '--as-recipe', action='store_true',
                        help='Transform the CSV to a recipe import.')
    parser.add_argument('csv_name', metavar='csv-name',
                        type=Path, nargs='?', default=CSV_FILE,
                        help=f'The name of the saved spreadsheet tab (from "File > Save a Copy..."). [{CSV_FILE}]')

    return parser.parse_args()

def write_recipe(args):
    """Write a recipe JSON file."""
    def all_ingredients():
        for step in card.recipe.values():
            yield from step

    def amount(key):
        return float(ingredient[key] or 0) / 100

    card = recipe_lib.parse_recipe_csv(args.csv_name, args)
    #pp(dict(card))
    #pp(dict(card.recipe))
    #pp(list(all_ingredients()))

    items = []
    for ingredient in all_ingredients():
        if not int(ingredient.get('counts?') or '0'):
            continue
        if not ingredient.get('unit') in {'g', 'ml'}:
            continue

        item = RECIPE_ITEM.format(
            name=ingredient['ingredients'].rsplit('[', 1)[0],
            amount=float(ingredient['amount'] or 0),
            #comment=ingredient['comment'],
            #fat=amount('fat'),
            #salt=amount('salt'),
        )
        items.append(item)

    data = RECIPE_BODY.format(
        title=card.lines[0].lstrip('#').strip(),
        items=',\n    '.join(items),
    )
    print(data)

    """{'ingredients': 'Cream 32% [REWE Beste Wahl]',
        'amount': '25',
        'unit': 'ml',
        'step': '3',
        'kcal': '311.00',
        'fat': '32.00',
        'carbs': '3.20',
        'sugar': '3.20',
        'protein': '2.50',
        'salt': '0.13',
        'fpdf': '0.03',
        'msnf': '6.32',
        'comment': '',
        '0carb[%]': '',
        'counts?': '1'},"""

def main():
    """Main loop."""
    args = parse_cli()
    if not any(v for k, v in vars(args).items() if k.startswith('as_')):
        args.as_recipe = True
    #pp(args)
    args.macros = False

    if args.as_recipe:
        write_recipe(args)
    else:
        recipe_lib.abort('Unknown or unimplemented target format!')

if __name__ == '__main__':
    main()
