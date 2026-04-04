---
applyTo: "**/*.py"
---
# Python Coding Style Standards

When generating or refactoring Python code, strictly adhere to the following formatting standards (aligned with PEP 8).

Generate code that is deterministic, minimizes vertical whitespace, and prioritizes code structure over 'pretty' alignment of variables.

## 1. Line Length & Wrapping
* **Max Line Length:** Limit lines to **110 characters**.
* **Wrapping Style:** Use **implied line continuation** inside parentheses, brackets, and braces rather than backslashes (`\`).
* **Trailing Commas:** Use trailing commas in multi-line collections (lists, dicts, function calls) to ensure the closing bracket sits on its own line. Include a trailing comma even for single-item collections to maintain consistency, and use one on the last item.

## 2. Indentation & Spacing
* **Indentation:** Strictly use **4 spaces** per indentation level. Never use tabs.
* **Binary Operators:** Break lines **before** a binary operator (e.g., `+`, `==`, `and`) to improve readability.
* **Whitespace:**
    * One space around operators (`n = 1`, not `n=1`).
    * No whitespace immediately inside parentheses `( item )` or before a comma/colon.
    * Two blank lines between top-level functions and classes; one blank line between methods inside a class.
    * No trailing whitespace at the end of lines.
* **End of File:** Exactly one blank line at the end of files.

## 3. Quotes & String Formatting
* **Quote Style:** Prefer **double quotes** (`"`) for strings unless the string contains double quotes, in which case use single quotes (`'`) to avoid escaping.
* **Docstrings:** Always use triple double quotes (`"""`) for docstrings. For multi-line docstrings, use this template:

```python
""" Brief description of the function/class/module.

    More detailed explanation and argument descriptions if necessary.
"""
```
* **F-Strings:** Use f-strings for string interpolation (e.g., `f"Value: {value}"`) instead of older methods like `str.format()` or `%` formatting.

## 4. Import Organization
* **Grouping:** Group imports in the following order, separated by a single blank line:
    1.  Standard library imports.
    2.  Related third-party imports.
    3.  Local application/library specific imports.
* **Sorting:** Sort imports by module name length and then alphabetically within each group.
* **Import Style:** Use `from module import ...` rather than comma-separated multiple imports on one line if they belong to different modules.

## 5. Type Annotations
* **Spacing:** Use a colon followed by a space for variables (`x: int = 10`). For return types, use a space before and after the arrow (`def func() -> None:`).

## 6. Comments
* **Inline Comments:** Use inline comments sparingly and only when the code is not self-explanatory. Start with a capital letter and be concise.
* **Block Comments:** Use block comments to explain complex logic or important details. Each line should start with a `#` and a single space, and the comment should be indented to the same level as the code it describes.
* **Trailing Comments:** Trailing comments should be separated by at least two spaces from the statement and start with a `#`.
