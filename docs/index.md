# About
A collection of my tested / approved Ninja Creami recipes.

> <img width=720 alt="Gelato Cart" src="https://raw.githubusercontent.com/jhermann/ice-creamery/refs/heads/main/assets/gelato-cart.webp" />

## How to Use This Site?
Use the top bar to navigate using [Tags](tags/) or the first letter of a recipe name.

> 💡 You can load <a href="/ice-creamery/print_page/" target="_blank">all pages at once<sup>↗</sup></a>
> to save the site as stand-alone HTML or PDF.

Check out the [Info](info/) section to get background information on the 'philosophy'
behind the specific formulation of these recipes, the ingredients used, and some tips & tricks
to successfully redproduce them in your kitchen.

That section also contains a FAQ page and a glossary, in case some abbreviations used arer unknown to you.

## How It's Made?
This website is based on a collection of calculated recipes stored in a
[GitHub repository](https://github.com/jhermann/ice-creamery#readme).

```embed
url: https://github.com/jhermann/ice-creamery#readme
```

The recipes are written as *LibreOffice* spreadsheets, which allows to directly
use formulas for the calculation of important ice cream metrics and nutritional information.

A Python script then converts CSV exports of the spreadsheets to markdown files, which are in turn used to render this HTML web site using
[MkDocs](https://github.com/mkdocs/mkdocs#readme).

```embed
url: https://www.mkdocs.org/
```
