# Copilot Instructions for ice-creamery

## Build, Test, and Lint Commands

- **Install dependencies:**
  ```sh
  python3 -mpip install -r ./requirements.txt
  ```
- **Run all tests:**
  ```sh
  pytest
  ```
- **Run a single test file:**
  ```sh
  pytest tests/test_utils.py
  ```
- **Linting:**
  - Follow PEP 8 and the custom rules in `.github/instructions/python-style.instructions.md`.

## High-Level Architecture

- **Recipes** are stored as Markdown files in `recipes/*/README.md`, generated from LibreOffice spreadsheets (see `recipes/Ice-Cream-Recipes.fods`).
- **Scripts** in `scripts/` automate:
  - Converting recipe sheets to Markdown (`ice-cream-recipe.py`)
  - Managing and searching recipe sheets (`recipe.py`)
  - Aggregating docs/recipes into summary files (`update-all-md.sh`)
- **Shared utilities** for scripts are in `scripts/_utils.py`.
- **Testing** uses `pytest` with tests in `tests/`, following strict conventions (see `.github/instructions/python-tests.instructions.md`).
- **Docs** are built with MkDocs (`mkdocs.yml`).
- **Info graphics** (e.g., `assets/Mindmap-Creami-Lab-core.png`) summarize the core concepts: ingredient roles, process mechanics, and key formulation principles for Ninja Creami recipes.

## Key Conventions

- **Python:**
  - Use only `pytest` for tests; place fixtures in `tests/conftest.py`.
  - Adhere to the style and test rules in `.github/instructions/python-style.instructions.md` and `.github/instructions/python-tests.instructions.md`.
- **Recipe workflow:**
  - Edit recipes in the spreadsheet, export as CSV, then convert to Markdown using `scripts/ice-cream-recipe.py`.
  - Ingredient and process conventions are visualized in `assets/Mindmap-Creami-Lab-core.png`.
- **Docs:**
  - Use MkDocs Material theme. Serve locally with:
    ```sh
    ./linkdocs.sh && mkdocs serve 2>&1 | grep -v 'INFO.*absolute link'
    ```
- **Security:**
  - Follow `.github/instructions/secure-development.instructions.md` for all code changes.
