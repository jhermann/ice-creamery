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
import subprocess

from pprint import pp  # pylint: disable=unused-import
from pathlib import Path
from collections import defaultdict

import yaml

CSV_FILE = 'Ice-Cream-Recipes.csv'  # TODO: add argument parsing
MD_FILE = 'recipe-{file_title}.md'

TAG_LIGHT_KCAL_LIMIT = 75.0
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


def add_default_tags(md_text, docmeta):
    """Insert YAML metadata into generated markdown text."""
    md_text_words = set(re.split(r'[^-A-Za-z]+', md_text))
    md_text_words_lc = set(x.lower() for x in md_text_words)
    md_text_title_lc = md_text.splitlines()[0].lower()
    docmeta.setdefault('description', 'Recipe for the Ninja Creami Deluxe [24oz]')
    docmeta.setdefault('tags', ['Draft'])
    kcal = re.search(r'100g; ([.0-9]+) kcal;', md_text)
    if kcal and float(kcal.group(1)) <= TAG_LIGHT_KCAL_LIMIT:
        docmeta['tags'].append('Light')
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
        docmeta['tags'] = list(sorted(set(docmeta['tags'])))
        md_text = '---\n' + yaml.safe_dump(docmeta).rstrip() + '\n---\n' + md_text
    return md_text


def read_images():
    """Read IMG tags from readme."""
    filename = Path('README.md')
    result = []
    if filename.exists():
        result = [x for x in filename.read_text(encoding='utf-8').splitlines() if '<img ' in x]
    return result or ['> <img width=360 alt="Spun Ice Cream" src="" />']


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

    return result


def subtitle(text):
    """Create markdown for a recipe subtitle."""
    # TODO: add a `--format=reddit|generic` option
    return f'# {text.upper()}'  # This is optimized for Reddit
    #return f'**{text.upper()}**'  # This is what it should be, if the Reddit Markdown parser wouldn't suck


def markdown_file(title):
    """Return name of Markdown file for a given recipe title."""
    filename = MD_FILE.format(file_title="_".join(title.replace("(", "").replace(")", "").split()))
    try:  # automatic recipe git repo mode
        git_root = Path(subprocess.check_output('git rev-parse --show-toplevel'.split(), encoding='utf-8').rstrip())
        if git_root / 'recipes' == Path.cwd().parent:
            filename = 'README.md'
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return filename


def main():
    """Main loop."""
    tags_only = '--tags' in sys.argv  # XXX: very cheap cmd line arg parsing
    recipe = defaultdict(list)
    lines = []
    nutrition = []
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
    }
    premix = [
        ' 1. Add the prepared dry ingredients, and blend QUICKLY using an immersion blender on full speed.',
    ]
    freezing = [  # inserted before 'mix-in' step
        ' 1. Put on the lid, freeze for 24h, then spin as usual. Flatten any humps before that.',
        ' 1. Process with RE-SPIN mode when not creamy enough after the first spin.',
    ]
    soaking = [
        ' 1. After mixing, let the base sit in the fridge for at least 30min (better 2h),'
        ' for the seeds to properly soak. Stir before freezing.',
    ]
    special_directions = []
    STEP_PREP = 0
    STEP_WET = 1
    STEP_DRY = 2
    STEP_FILL = 3
    STEP_MIX_IN = 4

    def handle_top_row(row):
        '''Helper for non-ingredient row handling.'''
        nonlocal images

        if row[2] and 'MSNF' not in row[0]:  # structured / complex row
            line = [x.strip() for x in row]
            if line[0].endswith(':'):
                line[0] = f'**{line[0]}**'
            elif line[2] in {'g', 'ml'}:
                line = ' *', line[1].replace('.00', ''), line[2], line[0]
            lines.append(' '.join(line))
        elif row[1]:  # row with a value in the 2nd column
            nutrition.append(f'**{row[0].strip()}:** {row[1].strip()}')
            if any(row[2:]):
                aux_info = ' • '.join([''] + [x.strip() for x in row[2:] if x.strip()])
                if aux_info.startswith(' • g • '):
                    aux_info = aux_info[3:]
                nutrition[-1] += aux_info
        elif row[0]:  # non-empty text
            if '[brand names]' not in row[0]:
                lines.append(row[0].replace(' \n', '\n').strip())
        elif lines[-1] != '':  # empty row (1st one after some text)
            lines.append('')

        if lines and images and lines[-1] and not lines[-1].startswith('#'):
            lines.extend([''] + images)
            images = []

    images = read_images()
    docmeta = read_meta()
    #print(yaml.safe_dump(docmeta)); die

    with open(CSV_FILE, 'r', encoding='utf-8') as handle:
        reader = csv.reader(handle, delimiter=';')
        row = ''
        title = next(reader)[0]
        lines.extend([f'# {title}', ''])

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
            row = next(reader)
            #print('!', row)
            if row[0] == 'Ingredients':
                break  # pass header line to ingredients processing
            elif row[0].lstrip().startswith('1. '):
                special_directions.append(' ' + row[0].strip())
            else:
                handle_top_row(row)

        fields = [x.lower().replace('#', 'step') for x in row]
        #print(fields)

        # Read ingredients
        for row in reader:
            data = dict(zip(fields, row))
            if not data['step']:
                handle_top_row(row)
            elif data['ingredients']:
                if data['amount'].endswith('.00'):
                    data['amount'] = data['amount'][:-3]
                if data['amount'] and data['amount'] != '0':
                    step = int(data['step'])
                    recipe[step].append(data)

        # End of CSV processing
    #pp(recipe)

    # Add ingredient list
    lines.extend([subtitle('Ingredients'), '', 'ℹ️ Brand names are in square brackets `[...]`.'])
    for step, (name, directions) in enumerate(steps.items()):
        if not recipe[step]:  # no ingredients for this step?
            continue
        lines.extend(['', f'**{name}**', ''])
        for ingredient in recipe[step]:
            ingredient['spacer'] = '' if ingredient['unit'] in {'g', 'ml'} else ' '
            ingredient['amount'] = ingredient['amount'].replace(".50", ".5")
            lines.append('  - _{amount}{spacer}{unit}_ {ingredients}'.format(**ingredient))
            if ingredient['comment']:
                lines[-1] += f" • {ingredient['comment']}"

    # Add directions
    lines.extend(['', subtitle('Directions'), ''])
    if special_directions:
        lines.extend(special_directions)
        if any(x in line.lower().split() for line in special_directions for x in {'heat', 'cook'}):
            docmeta['tags'].append('Cooked Base')
    for step, (name, directions) in enumerate(steps.items()):
        if step == STEP_PREP:
            if recipe[STEP_PREP] and not any('water' in x['ingredients'].lower() for x in recipe[STEP_PREP]):
                continue
        if step == STEP_MIX_IN:
            if any('chia' in x['ingredients'].lower() for x in recipe[STEP_DRY]):
                lines.extend(soaking)
            lines.extend(freezing)
        if recipe[step]:  # we have ingredients for this step?
            for line in [x.strip() for x in directions.strip().splitlines()]:
                lines.append(f' 1. {line}')
        if step == STEP_WET:
            if recipe[STEP_PREP] and not any('water' in x['ingredients'].lower() for x in recipe[STEP_PREP]):
                lines.extend(premix)

    # Add nutritional info
    lines.extend(['', subtitle('Nutritional & Other Info'), '- ' + '\n- '.join(nutrition)])

    # Add default tags
    lines.append('')  # add trailing line end
    md_text = '\n'.join(lines)
    md_text = add_default_tags(md_text, docmeta)

    # Create the Markdown file
    md_file = markdown_file(title)
    md_text = md_text.replace('http://bit.ly/4frc4Vj', '[http﹕//bit.ly/4frc4Vj]'
        '(https://jhermann.github.io/ice-creamery/'
        'I/Ice%20Cream%20Stabilizer%20(ICS)/)')  # take care of Reddit stupidness
    if tags_only:
        md_text = Path(md_file).read_text(encoding='utf-8').splitlines()
        if md_text[0] == '---':
            for idx in range(1, len(md_text)):
                if md_text[idx] == '---':
                    del md_text[0:idx+1]
                    break
        md_text = '\n'.join(md_text).strip() + '\n'
        md_text = add_default_tags(md_text, docmeta)
        print(f'Updating tags only: {", ".join(sorted(docmeta["tags"]))}')
    with open(md_file, 'w', encoding='utf-8') as out:
        out.write(md_text)

    # Open markdown file in VS Code
    os.system(f'{os.getenv("GUI_EDITOR", "code")} "{md_file}"')

if __name__ == '__main__':
    main()
