# ice-creamery
> A collection of my tested / approved Ninja Creami recipes.

The [recipes](https://github.com/jhermann/ice-creamery/tree/main/recipes)
folder contains a
[template spreadsheet](https://github.com/jhermann/ice-creamery/blob/main/recipes/Ice-Cream-Recipes.fods)
for LibreOffice, with a full ingredients list of brands
as available to me in Germany. You can re-use generic rows like
"Strawberries", and also add your own brands.

> <img width=320 alt="spreadsheet-template" src="https://github.com/jhermann/ice-creamery/blob/main/assets/spreadsheet-template.png?raw=true" />

The [Open Food Facts](https://world.openfoodfacts.org/)
website and app makes this more efficient than dragging
half of your fridge's and cupboards' contents to your computer. 😉

The [scripts](https://github.com/jhermann/ice-creamery/tree/main/scripts)
folder has some utilities, right now a script to convert a recipe sheet
to its [Markdown rendering](https://github.com/jhermann/ice-creamery/blob/main/recipes/Cherry%20Ice%20Cream%20(Deluxe)/README.md).

## Structure of the recipe spreadsheet

**TODO**

The *freezing point depression factor* (FPDF) is a key indicator towards
the softness of the frozen base at serving temperature (typically -12°C).
It is given relative to the effect table sugar (sucrose) has on the freezing point,
and ranges from inulin with 0.1 to pure ethanol at 7.4.

To evaluate the expected softness of a base, the *total* FPDF is calculated
from the weight of ingredients, as the sum of `weight[g] * specific FPDF`
over all sugars / sweeteners (in 100g of ice cream mix), with lactose typically
included in the EU (PAC value).

Ice cream stored at -18°C with a total FPDF of 20..25 will be easily scoopable,
while bases with TFPDF<15 will be quite hard. Ice cream is considered soft enough
when about 65% of the contained water molecules are frozen at serving temperature.


## How to convert a recipe to Markdown?

**TODO** (save sheet as CSV and use the
[ice-cream-recipe.py](https://github.com/jhermann/ice-creamery/blob/main/scripts/ice-cream-recipe.py) script)


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
