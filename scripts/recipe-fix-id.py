#! /usr/bin/env python3
"""Fill missing recipe ingredient IDs from the canonical catalog CSV."""

from __future__ import annotations

import argparse
import csv
import io

from pathlib import Path
from tempfile import NamedTemporaryFile


CATALOG_PATH = Path(__file__).resolve().with_name("Ice-Cream-Recipes.csv")
RECIPE_HEADER_PREFIX = "Ingredients;Amount;"


def detect_newline(path: Path) -> str:
    """Detect dominant newline style for output consistency."""
    sample = path.read_bytes()[:65536]
    if b"\r\n" in sample:
        return "\r\n"
    return "\n"


def sniff_dialect(path: Path) -> csv.Dialect:
    """Infer CSV dialect from file contents."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        sample = handle.read(65536)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        class Fallback(csv.Dialect):
            delimiter = ";"
            quotechar = '"'
            doublequote = True
            skipinitialspace = False
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL

        return Fallback()


def normalize_header(value: str) -> str:
    """Normalize header names for case-insensitive lookup."""
    return value.strip().lower()


def find_column_index(row: list[str], name: str) -> int:
    """Return the index of a header column, matched case-insensitively."""
    needle = normalize_header(name)
    for index, value in enumerate(row):
        if normalize_header(value) == needle:
            return index
    raise KeyError(f"Column not found: {name}")


def load_catalog_ids(path: Path, ingredient_column: str, id_column: str) -> dict[str, str]:
    """Load ingredient IDs from the canonical catalog CSV."""
    mapping: dict[str, str] = {}
    dialect = sniff_dialect(path)

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, dialect)
        header: list[str] | None = None
        ingredient_index = -1
        id_index = -1

        for row in reader:
            if not row:
                continue
            try:
                ingredient_index = find_column_index(row, ingredient_column)
                id_index = find_column_index(row, id_column)
                header = row
                break
            except KeyError:
                continue

        if header is None:
            raise ValueError(f"Catalog header not found in {path}")

        for row in reader:
            if len(row) <= ingredient_index:
                continue
            ingredient_name = row[ingredient_index].strip()
            if not ingredient_name:
                continue
            ingredient_id = row[id_index].strip() if len(row) > id_index else ""
            if not ingredient_id:
                continue
            existing_id = mapping.get(ingredient_name)
            if existing_id and existing_id != ingredient_id:
                raise ValueError(
                    f"Conflicting IDs for ingredient {ingredient_name!r}: {existing_id!r} vs {ingredient_id!r}"
                )
            mapping[ingredient_name] = ingredient_id

    return mapping


def update_csv(path: Path, ingredient_column: str, id_column: str, catalog_ids: dict[str, str]) -> tuple[int, int, int]:
    """Update a CSV in place and return (rows, filled_ids, missing_matches)."""
    newline = detect_newline(path)
    dialect = sniff_dialect(path)
    row_count = 0
    filled_count = 0
    missing_matches = 0

    with path.open("r", encoding="utf-8", newline="") as src:
        lines = src.readlines()
    header_line_index = next(
        (index for index, line in enumerate(lines) if line.startswith(RECIPE_HEADER_PREFIX)),
        None,
    )
    if header_line_index is None:
        raise ValueError(f"Recipe header line starting with {RECIPE_HEADER_PREFIX!r} not found in {path}")

    preamble_lines = lines[:header_line_index]
    csv_text = "".join(lines[header_line_index:])
    reader = csv.reader(io.StringIO(csv_text), dialect)
    try:
        header = next(reader)
    except StopIteration as exc:
        raise ValueError(f"CSV has no header row: {path}") from exc

    ingredient_index = find_column_index(header, ingredient_column)
    try:
        id_index = find_column_index(header, id_column)
        has_id_column = True
    except KeyError:
        id_index = len(header)
        header = [*header, id_column]
        has_id_column = False

    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        delete=False,
    ) as dst:
        tmp_path = Path(dst.name)
        for line in preamble_lines:
            dst.write(line)

        writer = csv.writer(
            dst,
            dialect=dialect,
            lineterminator=newline,
        )
        writer.writerow(header)

        for row in reader:
            row = list(row)
            if not has_id_column:
                row.extend([""] * (len(header) - len(row)))
            elif len(row) <= id_index:
                row.extend([""] * (id_index + 1 - len(row)))

            ingredient_name = row[ingredient_index].strip() if len(row) > ingredient_index else ""
            current_id = row[id_index].strip() if len(row) > id_index else ""
            lookup_id = catalog_ids.get(ingredient_name, "")

            if not current_id and lookup_id:
                row[id_index] = lookup_id
                filled_count += 1
            elif not current_id and ingredient_name:
                missing_matches += 1

            writer.writerow(row)
            row_count += 1

    tmp_path.replace(path)
    return row_count, filled_count, missing_matches


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Add or fill missing ingredient IDs from the canonical catalog CSV.",
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default="Ice-Cream-Recipes.csv",
        help="Path to the recipe CSV file to update in place (default: Ice-Cream-Recipes.csv).",
    )
    parser.add_argument(
        "--ingredient-column",
        default="ingredients",
        help="Ingredient source column in the target CSV (default: ingredients).",
    )
    parser.add_argument(
        "--catalog-ingredient-column",
        default="Ingredients",
        help="Ingredient column in the catalog CSV (default: Ingredients).",
    )
    parser.add_argument(
        "--id-column",
        default="ID",
        help="Target ID column name (default: ID).",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entrypoint."""
    args = parse_args()
    csv_path = Path(args.csv_file).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog CSV not found: {CATALOG_PATH}")

    catalog_ids = load_catalog_ids(
        path=CATALOG_PATH,
        ingredient_column=args.catalog_ingredient_column,
        id_column=args.id_column,
    )
    rows, filled, missing = update_csv(
        path=csv_path,
        ingredient_column=args.ingredient_column,
        id_column=args.id_column,
        catalog_ids=catalog_ids,
    )
    print(
        f"Processed {rows} rows in {csv_path}; filled {filled} IDs; "
        f"left {missing} unmatched ingredient rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
