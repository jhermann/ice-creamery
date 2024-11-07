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
import csv
import subprocess

from pathlib import Path
from collections import defaultdict

CSV_FILE = 'Ice-Cream-Recipes.csv'  # TODO: add argument parsing
MD_FILE = 'recipe-{file_title}.md'


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
    recipe = defaultdict(list)
    lines = []
    nutrition = []
    steps = {  # These correlate to the "#" column in the sheet's ingredient list, with prep ~ 0 and mix-in ~ 4
        'prep': 'Prepare the ingredients, e.g. bloom the cocoa.',
        'wet': 'Add "wet" ingredients to empty Creami tub.',
        'dry': """
            Weigh and mix dry ingredients, easiest by adding to a jar with a secure lid and shaking vigorously.
            Pour into the tub and *QUICKLY* use an immersion blender on full speed to homogenize everything.
            Let blender run until thickeners are properly hydrated, up to 1-2 min. Or blend again after waiting that time.
        """,
        'top off': 'Add remaining ingredients (to the MAX line) and stir with a spoon.',
        'mix-in':
            'Process with MIX-IN after adding mix-ins evenly.'
            ' For that, add partial amounts into a hole going down to the bottom, and fold the ice cream over, building pockets of mix-ins.',
    }
    freezing = [  # inserted before 'mix-in' step
        ' 1. Put on the lid, freeze for 24h, then spin as usual. Flatten any humps before that.',
        ' 1. Process with RE-SPIN mode when not creamy enough after the first spin.',
    ]
    STEP_MIX_IN = 4

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

        # Skip to ingredient list
        while row[0] != 'Ingredients':  # process comment / text lines, up to the ingredient list
            row = next(reader)
            #print('!', row)
            if row[0] == 'Ingredients':
                break  # pass header line to ingredients processing
            elif row[2] and 'MSNF' not in row[0]:  # structured / complex row
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

        fields = [x.lower().replace('#', 'step') for x in row]
        #print(fields)

        # Read ingredients
        for row in reader:
            data = dict(zip(fields, row))
            if data['ingredients']:
                if data['amount'].endswith('.00'):
                    data['amount'] = data['amount'][:-3]
                if data['amount'] and data['amount'] != '0':
                    step = int(data['step'])
                    recipe[step].append(data)

        # End of CSV processing
    #print('I =', recipe[1][0])

    # Add ingredient list
    lines.extend([subtitle('Ingredients'), '', 'ℹ️ Brand names are in square brackets `[...]`.'])
    for step, (name, directions) in enumerate(steps.items()):
        if not recipe[step]:  # no ingredients for this step?
            continue
        lines.extend(['', f'**{name.title()}**', ''])
        for ingredient in recipe[step]:
            lines.append('  - _{amount}{unit}_ {ingredients}'.format(**ingredient))
            if ingredient['comment']:
                lines[-1] += f" • {ingredient['comment']}"

    # Add directions
    lines.extend(['', subtitle('Directions'), ''])
    for step, (name, directions) in enumerate(steps.items()):
        if step == STEP_MIX_IN:
            lines.extend(freezing)
        if recipe[step]:  # we have ingredients for this step?
            for line in [x.strip() for x in directions.strip().splitlines()]:
                lines.append(f' 1. {line}')

    # Add nutritional info
    lines.extend(['', subtitle('Nutritional & Other Info'), '- ' + '\n- '.join(nutrition)])

    # Create the Markdown file
    lines.append('')  # add trailing line end
    md_file = markdown_file(title)
    md_text = '\n'.join(lines)
    md_text = md_text.replace('http://bit.ly/4frc4Vj', '[http﹕//bit.ly/4frc4Vj]'
        '(https://github.com/jhermann/ice-creamery/tree/main/'
        'recipes/Ice%20Cream%20Stabilizer%20%28ICS%29)')  # take care of Reddit stupidness
    with open(md_file, 'w', encoding='utf-8') as out:
        out.write(md_text)

    # Open markdown file in VS Code
    os.system(f'{os.getenv("GUI_EDITOR", "code")} "{md_file}"')

if __name__ == '__main__':
    main()
