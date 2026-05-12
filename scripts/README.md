# Scripts & Tools <!-- omit from toc -->

**Contents**

- [Overview](#overview)
- [Building a Gemini "Ice Cream Specialist" Gem](#building-a-gemini-ice-cream-specialist-gem)
  - [Example](#example)
  - [Setup](#setup)

## Overview

This folder contains utilities for recipe conversion, search, metadata cleanup, and docs aggregation.

- [Ice-Cream-Recipes.csv](./Ice-Cream-Recipes.csv): CSV export of the LibreOffice recipe workbook used as script input.
- [icc-tool.py](./icc-tool.py): Helper CLI for icecreamcalc imports; converts recipe CSV data to JSON import payloads.
- [ice-cream-recipe.py](./ice-cream-recipe.py): Main converter that generates Markdown recipes from spreadsheet CSV exports.
- [nutrition-db.csv](./nutrition-db.csv): Nutrition reference table used by recipe tooling for macro and ingredient metadata.
- [recipe.py](./recipe.py): Spreadsheet utility CLI to list/search/open recipe sheets and manage related config/actions.
- [reddit-png.sh](./reddit-png.sh): Renders README sections to PNG screenshots (via pandoc/chromium) for sharing.
- [update-all-md.sh](./update-all-md.sh): Aggregates docs, recipe READMEs, and wiki Markdown files into project-wide summary text files.

## Building a Gemini "Ice Cream Specialist" Gem

Use when formulating, optimizing, or troubleshooting ice cream and gelato recipes, including PAC/POD balance, freezing curves, solids, texture, overrun, stabilizers, scoopability, meltdown, and process variables.

### Example

----
> 🤖🔷 give me a vanilla protein ice cream 460g batch size, just the ingredients table

Here is a balanced, high-protein vanilla ice cream recipe formulated for a standard **460g batch** (perfect for a Ninja Creami pint or traditional churner).

**Vanilla Protein Ice Cream Ingredients (460g Batch)**

| Ingredient | Amount | Purpose / Notes |
| :--- | :--- | :--- |
| **Fairlife Ultra-Filtered Milk (2% or Whole)** | 300g | High-protein liquid base; provides a creamy texture |
| **Vanilla Whey/Casein Blend Protein Powder** | 35g | The primary protein source (approx. one scoop) |
| **Heavy Whipping Cream** | 40g | Adds necessary fat for a smooth, scoopable mouthfeel |
| **Allulose (or sweetener of choice)** | 40g | Sweetness and lowers freezing point (keeps it soft) |
| **Vanilla Extract (or Vanilla Bean Paste)** | 5g (1 tsp) | Rich, authentic vanilla flavor |
| **Tara Gum or Xanthan Gum** | 1g (approx. 1/4 tsp) | Stabilizer to prevent icy texture and mimic commercial ice cream |
| **Salt** | 1g (a pinch) | Enhances flavor and sweetness |
| **Total Weight** | **460g** | |

----
> 🤖🔷 show total kcal, fat, sugar, and PAC/POD normalized to 100g

🗒️ *Note on PAC and POD: These values are normalized to sucrose (table sugar), which has a baseline PAC (freezing point depression factor) of 100 and a POD (sweetening power) of 100.*

| Metric | Value per 100g | Notes / Contribution Breakdown |
| :--- | :--- | :--- |
| **Total Energy** | **78.4 kcal** | Primarily from the protein powder and milk |
| **Fat** | **3.8g** | ~3.1g from heavy cream; ~0.7g from milk/protein powder |
| **Sugar (Lactose)** | **2.0g** | Natural dairy sugars (1.7g from Fairlife milk, 0.3g from cream) |
| **Added Sugar** | **0g** | Sweetened entirely with allulose |
| **PAC** *(Freeze Depression)* | **23.5** | **Highly scoopable.** Driven almost entirely by the allulose ($190 \times 8.7\%$) |
| **POD** *(Sweetening Power)* | **8.6** | **Mildly sweet.** Clean and balanced sweetness |

💡 **Freezing Tip:** A PAC value of **23.5** is excellent for low-fat, high-protein ice creams. It ensures that even without traditional sugar and high fat, your batch will spin incredibly smooth in a Ninja Creami or scoop easily out of a standard home freezer without turning into a solid block of ice.

### Setup

This is not an intro course to AI, Gemini, NotebookLM, Gems, Skills, Python & bash development, and all the other stuff you (might) need to know. Also I'm not your tutor.

All described calls work on Win11/WSL2, but should easily transfer to any POSIX environment.

You were warned, there be dragons! 🐉

----
Create your *NotebookLM*:

1. Check out this repository.
2. Create a new notebook like "Deluxe Ice Cream and Sorbet Recipes".
3. Call `./scripts/update-all-md.sh` in the repo root, and then upload the created `all-*.txt` files as sources (3 text files).
4. Upload `./scripts/nutrition-db.csv` as a source.
5. Download the [AFCD Nutritional Database](https://jhermann.github.io/ice-creamery/info/web-resources/#nutritional-databases) (*AFCD Data Files*), unzip the data and upload `AFCD Release 3 - Nutrient profiles-l.csv`, `AFCD Release 3 - Nutrient profiles-2.csv`, and `AFCD Release 3 - Nutrient profiles-3.csv`. Those three files are exports of the different sheets in the `AFCD Release 3 - Nutrient profiles` spreadsheet.
7. You should now have 7 sources.

----
> 🤖📓 explain the sources, in a very terse form, just the facts

Nutrient profiles from the **[Australian Food Composition Database (AFCD)](https://afcd.foodstandards.gov.au/)** and custom files provide technical data like fat, sugar, and protein for thousands of ingredients. Expert science guides define scoopability through PAC (freezing point depression) and sweetness via POD so you can balance your base for the perfect texture.

Scientific wiki entries explain how stabilizers like Guar gum and GMS create a physical barrier to stop large ice crystals from forming. These facts are combined with practical machine safety tips and a collection of recipes scaled specifically for Ninja Creami Deluxe or Standard tubs.

----
Now create your *Gemini Gem*:

1. Add a new gem named "Ice Cream Specialist".
2. Describe it as "Use when formulating, optimizing, or troubleshooting ice cream and gelato recipes, including PAC/POD balance, freezing curves, solids, texture, overrun, stabilizers, scoopability, meltdown, and process variables."
3. Copy the [expert-glacier](https://github.com/jhermann/ice-creamery/blob/main/.github/skills/expert-glacier/SKILL.md) skill into the `Instructions` field.
4. Add your notebook as `Knowledge` (➕ button).
5. Save the Gem.
6. Try the example session from further above.
