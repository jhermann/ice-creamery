#! /usr/bin/env python3
"""
    Python script that spits out Markdown based on a Libreoffice spreadsheet
    (CSV export of a recipe sheet).

    Copyright (c) 2024 Jürgen Hermann

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
import difflib
import argparse
import subprocess

from pprint import pp  # pylint: disable=unused-import
from pathlib import Path
from operator import itemgetter
from collections import defaultdict

import yaml
from attrdict import AttrDict


CSV_FILE = 'Ice-Cream-Recipes.csv'
MD_FILE = 'recipe-{file_title}.md'
WEBSITE_BASE_URL = 'https://jhermann.github.io/ice-creamery'

TAG_LIGHT_KCAL_LIMIT = 75.0
TAG_SCOOPABLE_PAC_LIMIT = 30.0
PREPPED_NAME = {
    'ICSv2': 'Ice Cream Stabilizer (ICS)',
}
SNIPPETS = dict(
    alcohol="\n{% include 'assets/booze2vg.inc.md' %}\n",
)
PREPPED = {
    'ICSv2': {
        'Erythritol (E968)': 100.00,
        'Inulin': 100.00,
        'Tylose powder (E466, Tylo, CMC)': 10.00,
        'Guar gum (E412)': 3.50,
        'Salt': 3.50,
        'Xanthan gum (E415, XG)': 1.00,
    },
    'Salty Stability': {
        'Inulin': 110.00,
        'Glycerol Monostearate (GMS / E471)': 18.0,
        'Tylose powder (E466, Tylo, CMC)': 9.00,
        'Guar gum (E412)': 6.00,
        'Salt': 5.00,
        'Xanthan gum (E415, XG)': 2.00,
    },
}
DEFAULT_TAGS = set([
    'Allulose',
    'Erythritol',
    'Hi-Protein',
    'Low-Fat',
    'Low-Sugar',
    'Monk-Fruit',
    'Stevia',
    'Sucralose',
    'Xylitol',
    'Vanilla',
])
DEFAULT_TAGS_TITLE = set([
    'Sorbet',
])
DEFAULT_TAG_GROUPS = {
    'Dairy': set(['Dairy',
        'Buttermilk',
        'Cheese',
        'Sherbet',
    ]),
    'Emulsifier': set([
        'Glycerol Monostearate', 'GMS',
        'Lecithin',
    ]),
    'Fruit': set(['Fruit'
        'Apple', 'Apricot',
        'Banana', 'Blueberry',
        'Cherry',
        'Mandarin', 'Mango',
        'Orange',
        'Peach', 'Pineapple', 'Plum',
        'Strawberry',
        'Ube',
    ]),
    'Polysaccharide Gum': set([
        'LBG', 'Locust', 'Guar', 'Tara', 'XG', 'Xanthan',
    ]),
    'Sorbet': set(['Sherbet']),
}
DEFAULT_TAGS_EXACT = {
    '(Deluxe)': 'Deluxe',
    'CMC': 'Tylo Powder (CMC)',
}
# these are removed before adding them back (or not, when they do not apply any more)
CALCULATED_TAGS = {
    'Allulose',
    'Erythritol',
    'Hi-Protein',
    'Low-Fat',
    'Low-Sugar',
    'Light',
    'Monk-Fruit',
    'Scoopable',
    'Stevia',
    'Sucralose',
    'Xylitol',
}
AUTO_LINK_STOP_WORDS = {
    'Bean Powder', 'Beet Root', 'berry powder', 'Root powder', 'cream-filled',
    'Cherries, Sour', 'Condensed milk', 'Corn starch', 'Cream 32%', 'Cream Punch',
    'desiccated', 'Evaporated milk', 'Extract',
    'Flavor drops', 'Flavor Powder', 'Ice Cream', 'Irish Cream',
    'Low fat milk', 'Milk 3.5%', 'Mint chocolate',
    'Peanut butter', 'Philadelphia Milka', 'Printen',
    'Seed Powder', 'Soy sauce', 'tea powder', 'to MAX line',
}
LOGO_IMG = '<img style="float: right; margin-left: 1.5em;" width=240 alt="Logo" src="%s" />'
MILK_HINT = ('Soy milk 1.6%', '*alternative*: use any other preferred milk (~2% fat)')


def add_default_tags(md_text, docmeta):
    """Insert YAML metadata into generated markdown text."""
    md_text_words = set(re.split(r'[^-A-Za-z]+', md_text))
    md_text_words_lc = set(x.lower() for x in md_text_words)
    md_text_title_lc = md_text.splitlines()[0].lower()
    docmeta.setdefault('description', 'Recipe for the Ninja Creami Deluxe [24oz]')
    docmeta.setdefault('tags', ['Draft'])
    docmeta['tags'] = list(set(docmeta['tags']) - CALCULATED_TAGS)
    kcal = re.search(r'100g; ([.0-9]+) kcal;', md_text)
    if kcal and float(kcal.group(1)) <= TAG_LIGHT_KCAL_LIMIT:
        docmeta['tags'].append('Light')
    pac = re.search(r'FPDF / .?PAC.+:.?.? ([.0-9]+)', md_text)
    if pac and float(pac.group(1)) >= TAG_SCOOPABLE_PAC_LIMIT:
        docmeta['tags'].append('Scoopable')
    for tag in DEFAULT_TAGS:
        if tag.lower() in md_text_words_lc:
            docmeta['tags'].append(tag)
    for tag in DEFAULT_TAGS_TITLE:
        if tag.lower() in md_text_title_lc:
            docmeta['tags'].append(tag)
    for tag, group in DEFAULT_TAG_GROUPS.items():
        if any(word.lower() in md_text_words_lc for word in group):
            docmeta['tags'].append(tag)
    for word, tag in DEFAULT_TAGS_EXACT.items():
        if word in md_text_words:
            docmeta['tags'].append(tag)
    if docmeta:
        if 'excluded_tags' in docmeta:
            regex = re.compile(f"({')|('.join(docmeta['excluded_tags']).lower()})", flags=re.IGNORECASE)
            docmeta['tags'] = {x for x in docmeta['tags'] if not regex.search(x)}
        docmeta['tags'] = list(sorted(set(docmeta['tags'])))
        md_text = '---\n' + yaml.safe_dump(docmeta).rstrip() + '\n---\n' + md_text
    return md_text

def read_images():
    """Read IMG tags from readme."""
    filename = Path('README.md')
    result = {}
    if filename.exists():
        lines = filename.read_text(encoding='utf-8').splitlines()
        for idx, line in reversed(list(enumerate(lines))):
            if line == '---':
                lines = lines[idx+1:]
                break
        result = {n : x for n, x in enumerate(lines) if '<img ' in x}
    if 1 not in result: # no logo yet
        imgnames = [x for x in sorted(Path('.').glob('logo-*.*')) if x.suffix in {'.png', '.jpg', '.jpeg', '.webp'}]
        if imgnames:
            result[1] = LOGO_IMG % str(imgnames[0])
    if not (set(result) - {1}):
        result[997] = '> <img width=220 alt="After Sorbet" src="_1.jpg" class="zoomable" />'
        result[998] = '> <img width=220 alt="After Mix-in" src="_2.jpg" class="zoomable" />'
        result[999] = '> <img width=220 alt="Scooped" src="_3.jpg" class="zoomable" />'
    return result

def read_meta():
    """Read metadata from readme."""
    result = {}
    filename = Path('README.md')

    if filename.exists():
        lines = filename.read_text(encoding='utf-8').splitlines()
        if lines and lines[0] == '---':
            with filename.open(mode='r', encoding='utf-8') as handle:
                loader = yaml.SafeLoader(handle)
                try:
                    if loader.check_node():
                        result = loader.get_data() or {}
                finally:
                    loader.dispose()

    result.setdefault('tags', ['Draft'])
    result.setdefault('excluded_tags', ['Vanilla'])
    result.setdefault('excluded_steps', ['^$'])
    return result

def md_anchor(title, _re=re.compile(r'([^a-z0-9]+)')):
    """Convert a readable title into an anchor."""
    return _re.subn('-', title.lower())[0].strip('-')

def parse_info_docs(kind, header):
    """Parse the Markdown file 'ingredients.md' for linking from recipes to it."""
    docsfile = Path(__file__).resolve().parent.parent / 'docs' / 'info' / f'{kind}.md'
    markup = docsfile.read_text(encoding='utf-8')
    titles = [x.lstrip('#').strip() for x in markup.splitlines() if x.startswith(header)]
    wordmap = {md_anchor(x): set(md_anchor(x).split('-')) for x in titles}
    parse_info_docs.wordmap[kind] = wordmap
    return wordmap
parse_info_docs.wordmap = defaultdict(dict)

def ingredient_link(ingredient, kind='ingredients', threshold=0.4, args=None):
    """Link a recognized ingredient, otherwise return the given text unchanged."""
    def targetted(label, href):
        'Helper.'
        label = label.replace("[", r"\[").replace("]", r"\]")
        if args.get('reddit'):
            href = WEBSITE_BASE_URL.rsplit('/', 1)[0] + href
        link = f'[{label}]({href})'
        if not args.get('reddit'):
            link += '{target="_blank"}<sup>↗</sup>'
        return link

    args = vars(args) if args else {}
    for key in PREPPED:
        if key in ingredient:
            key = PREPPED_NAME.get(key, key)
            return targetted(ingredient, f'/ice-creamery/{key[0].upper()}/{key.replace(" ", "%20")}/')

    if any(x in ingredient for x in AUTO_LINK_STOP_WORDS):
        return ingredient

    cleaned = ingredient.replace('Skim Milkpowder', 'skim milk powder SMP')  # legacy recipes
    for word in {'Amaretto', 'Batida', 'Brandy', 'Liqueur', 'Vodka', 'Rum'}:
        cleaned = cleaned.replace(word, 'Alcohol (Ethanol)')
    cleaned = cleaned.rsplit('[', 1)[0]  # strip off brand names in '[]'
    given = md_anchor(cleaned).split('-')
    scores = {}
    #print(parse_info_docs.wordmap[kind].items())
    for anchor, words in parse_info_docs.wordmap[kind].items():
        score = sum(len(difflib.get_close_matches(x, words, cutoff=0.8)) for x in given)
        score /= len(words)
        if score > threshold:
            scores[score] = anchor
            #print(score, anchor, ingredient)
    if scores:
        anchor = list(sorted(scores.items()))[-1][1]
        return targetted(ingredient, f'/ice-creamery/info/{kind}/#{anchor}')
    else:
        return ingredient

def info_link(term, args=None):
    """Link recognized terms within an info bullet."""
    well_known = {'MSNF', 'PAC'}
    for fragment in well_known:
        link = ingredient_link(fragment, kind='glossary', threshold=0.01, args=args)
        if link != fragment:
            term = term.replace(fragment, link)
    return term

def subtitle(text, is_topping=False):
    """Create markdown for a recipe subtitle."""
    # TODO: add a `--format=reddit|generic` option
    return (
        f"{'*' if is_topping else '# '}"
        f"{text if is_topping else text.upper()}"
        f"{'*' if is_topping else ''}")  # This is optimized for Reddit
    #return f'**{text.upper()}**'  # This is what it should be, if the Reddit Markdown parser wouldn't suck


def markdown_file(title, is_topping=False):
    """Return name of Markdown file for a given recipe title."""
    filename = MD_FILE.format(file_title="_".join(title.lower().rsplit('(', 1)[0].strip().split()))
    if not is_topping:
        try:  # automatic recipe git repo mode
            git_root = Path(subprocess.check_output('git rev-parse --show-toplevel'.split(), encoding='utf-8').rstrip())
            if git_root / 'recipes' == Path.cwd().parent:
                filename = 'README.md'
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    return filename

def abort(errmsg):
    """Exit the script."""
    print(f"ERROR: {errmsg}", file=sys.stderr)
    sys.exit(1)

def parse_cli(argv=None):
    """"""
    argv = argv or sys.argv
    parser = argparse.ArgumentParser(
        prog='ice-cream-recipe',
        description=__doc__.split('.', 1)[0].strip() + '.',
        epilog='See https://github.com/jhermann/ice-creamery/#readme for more.')

    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Do not write results to file system.')
    parser.add_argument('-E', '--no-edit', action='store_true',
                        help='Do not start the editor with a newly written recipe file.')
    parser.add_argument('-t', '--tags-only', action='store_true',
                        help='Only update the tags metadata section.')
    parser.add_argument('-r', '--reddit', action='store_true',
                        help='Use markup that is compatible to Reddit.')
    parser.add_argument('--macros', action='store_true',
                        help='Produce a table of macros for all given ingredients.')
    parser.add_argument('csv_name', metavar='csv-name',
                        type=Path, nargs='?', default=CSV_FILE,
                        help=f'The name of the saved spreadsheet tab (from "File > Save a Copy..."). [{CSV_FILE}]')

    return parser.parse_args()


def parse_recipe_csv(csv_name, args, images=[]):
    """Read in an exported recipe spread sheet."""

    def handle_top_row(row):
        '''Helper for non-ingredient row handling.'''
        nonlocal images

        if row[2] and 'MSNF' not in row[0] and 'ℹ️' not in row[0]:
            # structured / complex row, e.g. with formulas
            line = [x.strip() for x in row]
            if line[0].endswith(':'):
                line[0] = f'**{line[0]}**'
            elif line[2] in {'g', 'ml'}:
                line = ' *', line[1].replace('.00', ''), line[2], line[0]
            lines.append(' '.join(line))
        elif row[1] and row[0].strip():  # row with a value in the 2nd column
            nutrition.append(f'**{info_link(row[0].strip("ℹ️").strip(), args=args)}:** {row[1].strip()}')
            if any(row[2:]):
                aux_info = ' • '.join([''] + [x.strip() for x in row[2:] if x.strip()])
                if aux_info.startswith(' • g • '):
                    aux_info = aux_info[3:]
                if not row[1].strip():
                    aux_info = aux_info.strip().lstrip('•').strip()
                nutrition[-1] += aux_info
        elif row[0]:  # non-empty text
            if '[brand names]' not in row[0]:
                lines.extend(row[0].replace(' \n', '\n').strip().splitlines())
        elif lines[-1] != '':  # empty row (1st one after some text)
            lines.append('')

    recipe = defaultdict(list)
    lines = []
    nutrition = []
    special_prep = []
    special_directions = []
    freezing = [  # inserted before 'mix-in' step
        ' 1. Put on the lid, freeze for 24h, then spin as usual. Flatten any humps before that.',
        ' 1. Process with RE-SPIN mode when not creamy enough after the first spin.',
    ]

    with open(csv_name, 'r', encoding='utf-8') as handle:
        reader = csv.reader(handle, delimiter=';')
        row = ''
        title = next(reader)[0]
        is_topping = title.endswith('Topping)') or title.endswith('Mix-in)')
        if is_topping:
            if 999 in images:
                # No default image
                del images[999]
            if not title.endswith(' (Mix-in)'):
                title = title.rsplit('(', 1)[0].strip()
        lines.extend([f"#{'#' if is_topping else ''} {title}", ''])
        if 1 in images:
            lines[-1:-1] = [images[1]]
            del images[1]

        # Handle nutrients
        next(reader)  # skip empty row
        fields = next(reader)[5:]  # nutrient column headers, followed by 3 lines with 100g/360g/total values
        while True:
            row = next(reader)
            if 'Nutritional' not in row[0]:
                break  # end of nutrient / macros info
            data = dict(zip(fields, row[5:]))
            nutrients = "; ".join([f'{k.lower()} {v}g' for k, v in data.items() if v])
            nutrition.append(f'**{row[0]}:** {row[1]}{row[2]}; {row[4]} kcal; {nutrients}')

        # Parse up to ingredient list
        while row[0] != 'Ingredients':  # process comment / text lines, up to the ingredient list
            img_idx = min(images) if images else 9999
            #print('L:', len(lines), 'I:', img_idx); pp(lines[-3:])
            if images and len(lines) >= img_idx:
                lines[img_idx:img_idx] = [images[img_idx], '']
                del images[img_idx]

            row = next(reader)
            #print('!', row)
            if row[0] == 'Ingredients':
                break  # pass header line to ingredients processing
            elif row[0].lstrip().startswith('1. '):
                if 'prep' in row[0]:
                    special_prep.append(' ' + row[0].strip())
                elif 'Before freezing' in row[0]:
                    freezing[0:0] = [' ' + row[0].strip()]
                elif ' a mix-in' in row[0] or ' the mix-in' in row[0]:
                    mix_in[0:0] = [' ' + row[0].strip()]
                else:
                    special_directions.append(' ' + row[0].strip())
            else:
                handle_top_row(row)

        if images:
            lines.extend([''] + list(images.values()))
            images = {}

        fields = [x.lower().replace('#', 'step') for x in row]
        #print(fields)

        # Read ingredients
        for row in reader:
            data = dict(zip(fields, row))
            if MILK_HINT[0] in data['ingredients'] and not data['comment']:
                data['comment'] = MILK_HINT[1]
            if not data['step']:
                handle_top_row(row)
            elif data['ingredients'] and data['counts?'] != '0':
                if data['amount'].endswith('.00'):
                    data['amount'] = data['amount'][:-3]
                if args.macros or data['amount'] and data['amount'] != '0':
                    step = int(data['step'])
                    recipe[step].append(data)

        # End of CSV processing

    return AttrDict(dict(
        recipe=recipe,
        lines=lines,
        nutrition=nutrition,
        special_prep=special_prep,
        special_directions=special_directions,
        freezing=freezing,
        is_topping=is_topping,
        title=title,
    ))


def main():
    """Main loop."""
    args = parse_cli()
    #pp(args)
    steps = {  # These correlate to the "#" column in the sheet's ingredient list, with prep ~ 0 and mix-in ~ 4
        'Prep': 'Prepare specified ingredients by dissolving / hydrating in hot water.',
        'Wet': 'Add "wet" ingredients to empty Creami tub.',
        'Dry': """
            Weigh and mix dry ingredients, easiest by adding to a jar with a secure lid and shaking vigorously.
            Pour into the tub and *QUICKLY* use an immersion blender on full speed to homogenize everything.
            Let blender run until thickeners are properly hydrated, up to 1-2 min. Or blend again after waiting that time.
        """,
        'Fill to MAX': 'Add remaining ingredients (to the MAX line) and stir with a spoon.',
        'Mix-ins':
            'Process with MIX-IN after adding mix-ins evenly.'
            ' For that, add partial amounts into a hole going down to the bottom, and fold the ice cream over, building pockets of mix-ins.',
        'Topping Options': '',
        'Optional / Choices': '',
    }
    premix = [
        ' 1. Add the prepared dry ingredients, and blend QUICKLY using an immersion blender on full speed.',
    ]
    soaking = [
        ' 1. After mixing, let the base sit in the fridge for at least 30min (better 2h),'
        ' for the seeds to properly soak. Stir before freezing.',
    ]
    mix_in = []
    STEP_PREP = 0
    STEP_WET = 1
    STEP_DRY = 2
    STEP_FILL = 3
    STEP_MIX_IN = 4

    images = read_images()
    docmeta = read_meta()
    parse_info_docs('ingredients', '### ')
    parse_info_docs('glossary', '## ')
    #print(yaml.safe_dump(docmeta)); die

    card = parse_recipe_csv(args.csv_name, args, images)
    recipe = defaultdict(list)
    recipe.update(card.recipe)
    lines, nutrition, special_prep, special_directions, is_topping, title = \
        list(card.lines), list(card.nutrition), \
        card.special_prep, card.special_directions, card.is_topping, card.title
    #pp(dict(card))
    #pp((dict(recipe), lines, nutrition))

    if 'Simple' in docmeta['tags']:
        lines.extend([
            '',
            "> ℹ️ Read [About 'Simple' Recipes](/ice-creamery/info/tips%2Btricks/#about-simple-recipes)"
            " regarding 'exotic' ingredients and their alternatives.",
            '',
        ])

    # Add ingredient list
    lines.extend([
        subtitle('Ingredients', is_topping),
        None if is_topping else '\nℹ️ Brand names are in square brackets `[...]`.'])
    for step, (name, directions) in enumerate(steps.items()):
        if not recipe[step]:  # no ingredients for this step?
            continue
        lines.extend([''] if is_topping else ['', f'**{name}**', ''])
        for ingredient in recipe[step]:
            ingredient['spacer'] = '' if ingredient['unit'] in {'g', 'ml', ''} else ' '
            ingredient['amount'] = ingredient['amount'].replace(".50", ".5")
            ingredient['href'] = ingredient_link(ingredient['ingredients'], args=args)
            lines.append('  - _{amount}{spacer}{unit}_ {href}'.format(**ingredient))
            if ingredient['comment']:
                lines[-1] += f" • {ingredient['comment']}"
            if not args.macros:
                for key in ('ICSv2', 'Salty Stability'):
                    if key in ingredient['ingredients']:
                        scale = float(ingredient['amount']) / sum(PREPPED[key].values())
                        nutrient = ' • '.join([f"{round(v * scale, 2 if v * scale < 1 else 1)}g {k}"
                                               for k, v in PREPPED[key].items()])
                        nutrition.append(f"**{ingredient['amount']}g '{key}' is:** {nutrient}.")
                        break

    # Add directions
    excluded_steps = re.compile(f"({')|('.join(docmeta.get('excluded_steps', [])).lower()})", flags=re.IGNORECASE)
    lines.extend(['', subtitle('Directions', is_topping), ''])
    if special_prep:
        lines.extend(special_prep)
    if special_directions:
        lines.extend(special_directions)
        if any(x in line.lower().split() for line in special_directions for x in {'heat', 'cook'}):
            docmeta['tags'].append('Cooked Base')
    if not is_topping:
        for step, (name, directions) in enumerate(steps.items()):
            if 'excluded_steps' in docmeta:
                directions = '\n'.join(line
                    for line in directions.splitlines()
                    if not excluded_steps.search(line))
            #if not directions:
            #    continue
            if step == STEP_PREP:
                if recipe[STEP_PREP] and not any('water' in x['ingredients'].lower() for x in recipe[STEP_PREP]):
                    continue
            elif step == STEP_MIX_IN:
                if any('chia' in x['ingredients'].lower() for x in recipe[STEP_DRY]):
                    lines.extend(soaking)
                lines.extend(card.freezing)
                lines.extend(mix_in)
            if recipe[step]:  # we have ingredients for this step?
                for line in [x.strip() for x in directions.strip().splitlines()]:
                    lines.append(f' 1. {line}')
            if step == STEP_WET:
                if recipe[STEP_PREP] and not any('water' in x['ingredients'].lower() for x in recipe[STEP_PREP]):
                    lines.extend([x for x in premix if not excluded_steps.search(x)])

    # Add nutritional info
    lines.extend([
        '', subtitle('Nutritional & Other Info', is_topping), '' if is_topping else None, '',
        '- ' + '\n- '.join(nutrition)])

    # Add default tags
    lines.append('')  # add trailing line end
    lines = [x for x in lines if x is not None]
    md_text = '\n'.join(lines)
    if not is_topping:
        md_text = add_default_tags(md_text, docmeta)

    # Create the Markdown file
    md_file = markdown_file(title, is_topping)
    md_text = md_text.replace('http://bit.ly/4frc4Vj', '[Ice Cream Stabilizer]'
        f'({WEBSITE_BASE_URL}'
        '/I/Ice%20Cream%20Stabilizer%20(ICS)/)')  # take care of Reddit stupidness

    if args.macros:
        def all_ingredients():
            'Helper.'
            for step in recipe.values():
                yield from step

        fields = dict(
            href='Ingredient' + '\u2001' * 15,
            kcal='Energy<br/>[kcal]',
            fat='',
            carbs='',
            sugar='',
            protein='',
            salt='',
            fpdf='PAC',
            msnf='MSNF',
            comment='',
        )
        header = ''.join([
            '\n', '| ', ' | '.join(v if v else k.title() for k, v in fields.items()), ' |',
            '\n', '| :--- |', ' ---: |' * (len(fields) - 2), ' :--- |',
        ])
        idx = 0
        print(header)
        for row in sorted(all_ingredients(), key=lambda x: x['ingredients'].lower()):
            if row['kcal']:
                if idx and not(idx % 10):
                    print(header)
                print('|', ' | '.join(row[x].replace(' [', '<br />[').replace(r' \[', r'<br />\[') for x in fields), '|')
                idx = idx + 1
        return

    if args.tags_only:
        md_text = Path(md_file).read_text(encoding='utf-8').splitlines()
        if md_text[0] == '---':
            for idx in range(1, len(md_text)):
                if md_text[idx] == '---':
                    del md_text[0:idx+1]
                    break
        md_text = '\n'.join(md_text).strip() + '\n'
        md_text = add_default_tags(md_text, docmeta)
        print(f'Updating tags only: {", ".join(sorted(docmeta["tags"]))}')

    snippet_re = '|'.join([re.escape(x) for x in SNIPPETS.keys()])
    snippet_re = f'<!-- SNIPPET: ({snippet_re}) -->'
    md_text, _ = re.subn('\n{2,}', '\n\n', md_text)
    md_text, _ = re.subn(r'(\d) • g', r'\1g', md_text)
    md_text, _ = re.subn(snippet_re, lambda x: SNIPPETS[x.group(1)].strip(), md_text)
    doc_start = md_text.find('\n---\n')
    for fragment in docmeta.get("remove", []):
        md_text = md_text[:doc_start] + md_text[doc_start:].replace(fragment, '')
    for fragment in docmeta.get("replace", []):
        orig, subst = re.split('=>', fragment, 1)
        md_text = md_text[:doc_start] + md_text[doc_start:].replace(orig, subst)

    if args.dry_run:
        print(md_text, end=None)
    else:
        with open(md_file, 'w', encoding='utf-8') as out:
            out.write(md_text)

        # Open markdown file in VS Code
        if not args.no_edit:
            os.system(f'{os.getenv("GUI_EDITOR", "code")} "{md_file}"')

if __name__ == '__main__':
    main()
