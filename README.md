> **ice-creamery** • A collection of my tested / approved Ninja Creami recipes.

> <img width=720 alt="Gelato Cart" src="https://raw.githubusercontent.com/jhermann/ice-creamery/refs/heads/main/assets/gelato-cart.webp" />

> 💡 See [GitHub pages](https://jhermann.github.io/ice-creamery/)
>  for a website with navigation and search.

> Copyright &copy; 2025 Jürgen Hermann
> <br />The content in `assets`, `docs`, and `recipes` is licensed under Creative Commons [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

**Contents**
- [What's this?](#whats-this)
- [Structure of the recipe spreadsheet](#structure-of-the-recipe-spreadsheet)
  - [The rows in the sheet](#the-rows-in-the-sheet)
  - [Freezing Point Depression Factor explained](#freezing-point-depression-factor-explained)
- [How to convert a recipe to Markdown?](#how-to-convert-a-recipe-to-markdown)
- [How to get a live version of a recipe?](#how-to-get-a-live-version-of-a-recipe)
- [Tips \& Tricks](#tips--tricks)
- [Setting up mkdocs](#setting-up-mkdocs)
- [Resources](#resources)


## What's this?

The [recipes](https://github.com/jhermann/ice-creamery/tree/main/recipes)
folder contains a
[template spreadsheet](https://github.com/jhermann/ice-creamery/blob/main/recipes/Ice-Cream-Recipes.fods)
for LibreOffice, with a full ingredients list of brands
as available to me in Germany. You can re-use generic rows like
"Strawberries", and also add your own brands.

The [Open Food Facts](https://world.openfoodfacts.org/)
website and app makes this more efficient than dragging
half of your fridge's and cupboards' contents to your computer. 😉

The [scripts](https://github.com/jhermann/ice-creamery/tree/main/scripts)
folder has some utilities, right now a script to convert a recipe sheet
to its [Markdown rendering](https://github.com/jhermann/ice-creamery/blob/main/recipes/Cherry%20Ice%20Cream%20(Deluxe)/README.md).

## Structure of the recipe spreadsheet

Each sheet in a *Calc* document based on the
[Ice-Cream-Recipes.fods](https://github.com/jhermann/ice-creamery/blob/main/recipes/Ice-Cream-Recipes.fods)
document is a duplicate of the template sheet. The script that converts a recipe to Markdown
relies on the structure described here, so you cannot easily change that without
also adapting the script.

> <img width=320 alt="spreadsheet-template" src="https://github.com/jhermann/ice-creamery/blob/main/assets/spreadsheet-template.png?raw=true" />

### The rows in the sheet

The first row contains the name of the recipe,
taken from the sheet name by default.

What follows is nutritional information for 100g, half a Deluxe tub,
and the total weight of a specific recipe. Note that only ingredients
measured in grams or milli-liters contribute to the total, drops, pinches
and so on are ignored. Anything measured in milli-liters is assumed
to have about the same density as water (i.e. 1g/cm³).

Where that is not really the case like with alcohol, you better
measure ingredients in grams on a scale, instead of volumetric measuring
that is so prevalent in the US. Some margin of error is acceptable here,
e.g. with alcohol-based vanilla extract that isn't used in large amounts anyway.

> ⚠️
> To adapt the template to a regular Creami,
> change `Deluxe` to `Regular` in row 1 of the sheet,
> and the 2nd row in the nutrients summary table.
> Also change the amount of 360g to 240g in that row,
> or another preferred serving size.

Below the macros, there is a formula for the total
*freezing point depression factor* (FPDF).
See the next section for details.

Then there are a few empty rows that can either contain text
(in the first column), that in Markdown is added below the
recipe title contributing to a recipe description or summary.

If the second column is also filled, the A and B columns are
interpreted as a key / value pair added to the final
*NUTRITIONAL & OTHER INFO* section of a recipe rendering.

Finally, you have the ingredients list with the name, amount & unit,
and further nutritional facts per 100g, one ingredient in each row.
The `#` column is a recipe step / ingredient type number:
0=prep, 1=wet, 2=dry, 3=top off, 4=mix-in.
The last column is a free-form comment field, added after the name
in the text version of the recipe.

### Freezing Point Depression Factor explained

The FPDF is a key indicator towards
the softness of the frozen base at serving temperature (typically -12°C).
It is given relative to the effect table sugar (sucrose) has on the freezing point,
and ranges from inulin with 0.1 to pure ethanol at 7.4.

To evaluate the expected softness of a base, the *total* FPDF is calculated
from the weight of ingredients, as the sum of `weight[g] * specific FPDF`
over all sugars / sweeteners (in 100g of ice cream mix), with lactose typically
included in the EU (PAC value). Apart from the lactose inclusion,
*Potere Anti Congelante* is just another name for FPDF.

Ice cream stored at -18°C with a total FPDF of 20..25 will be easily scoopable,
while bases with TFPDF<15 will be quite hard. Ice cream is considered soft enough
when about 65% of the contained water molecules are frozen at serving temperature.


## How to convert a recipe to Markdown?

To save a single recipe sheet as a CSV file and convert it to Markdown:

 1. Select *File > Save a Copy...* from the menu.
 1. Enter `Ice-Cream-Recipes.csv` as the file name, and choose `Text CSV` as the type, then press *Save*.
 1. Change export settings to match the ones shown below, then press *OK*.
 1. Call the [ice-cream-recipe.py](https://github.com/jhermann/ice-creamery/blob/main/scripts/ice-cream-recipe.py) script.
    It renders the Markdown file, and then opens your editor with it (`code` by default, unless the `GUI_EDITOR` envvar is set).

> ![save-as-csv settings](https://github.com/jhermann/ice-creamery/blob/main/assets/save-as-csv.png?raw=true)


## How to get a live version of a recipe?

Note that to get a version of
[recipes](https://github.com/jhermann/ice-creamery/tree/main/recipes)
that you can change and experiment with,
you can plug the ingredients list of a CSV file like
[Ice-Cream-Recipes.csv](https://github.com/jhermann/ice-creamery/blob/main/recipes/Cherry%20Ice%20Cream%20(Deluxe)/Ice-Cream-Recipes.csv)
into the template spreadsheet
[Ice-Cream-Recipes.fods](https://github.com/jhermann/ice-creamery/blob/main/recipes/Ice-Cream-Recipes.fods),
containing live formulas. Just load both files into *Calc*
and copy the ingredient rows in the CSV document to the FODS one.

This allows you to replace the nutritional information
with the values of the brands you can buy locally,
or experiment with alternatives and a different composition.

I did not test if Excel can read the FODS format properly,
but then the LibreOffice Suite is a free install that works
in parallel to a Microsoft Office installation.


## Tips & Tricks

 * It's recommended that, once a recipe is tested and approved,
 to sort the ingredients by the `#` column and then the `Amount`
 one (descending). This makes the recipe simple to use directly,
 without first converting it to Markdown.
 * Keep all your own recipes in a single ODS file,
 starting from the FODS template. Then duplicate
 the `Template` sheet, rename it to the recipe name, and fill in
 your amounts. After sorting like described right above, remove
 any rows with zero amounts.
 * Add journal entries to your sheet like this:

   > ![journal-entries](https://github.com/jhermann/ice-creamery/blob/main/assets/journal.png?raw=true)

   This is especially useful while experimenting and when
   you don't want to use `git` yet, where commit messages
   would take that place.


## Setting up mkdocs

To serve the recipe web site locally, you need to run the following commands.
Install the [mkvenv3](https://github.com/jhermann/ruby-slippers/blob/master/home/bin/mkvenv3)
script before that into your `~/bin`.

```sh
sudo apt install libgtk-4-dev libevent-dev libavif-dev
mkvenv3 mkdocs 'mkdocs-material[imaging]' \
    mkdocs-exporter mkdocs-git-revision-date-localized-plugin \
    mkdocs-link-embeds-plugin mkdocs-print-site-plugin mkdocs-macros-plugin
```

Then call the following command in the repository's root directory:

```sh
./linkdocs.sh && mkdocs serve 2>&1 | grep -v 'INFO.*absolute link'
```

You can also optionally create a PDF rendering into `site/.well-known/site.pdf`, using this command:

```sh
MKDOCS_EXPORTER_PDF=true mkdocs build
```

More plugins are available from the [catalog](https://github.com/mkdocs/catalog).


## Resources

 * [Ice Cream Science • Dream Scoops](https://www.dreamscoops.com/ice-cream-science/)
 * [Ice Cream @ Underbelly](https://under-belly.org/category/ice-cream/)
 * [Ruben Porto's Blog & Ice Cream Spreadsheet](https://www.icecreamscience.com/)
 * [What PAC Is, and How to Calculate It (Medium)](https://medium.com/@gelatologist/what-pac-is-and-how-to-calculate-it-2f1ade1bd5df)
 * [E numbers @ Wikipedia](https://en.wikipedia.org/wiki/E_number#E400%E2%80%93E499)
