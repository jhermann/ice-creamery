#! /usr/bin/env python3
"""Add a trailing ID column and fill only missing IDs from SHA-1(name)[:7]."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile


def detect_newline(path: Path) -> str:
    """Detect dominant newline style for output consistency."""
    sample = path.read_bytes()[:65536]
    if b"\r\n" in sample:
        return "\r\n"
    return "\n"


def short_sha1(text: str, length: int = 7) -> str:
    """Return the first N hex chars of a UTF-8 SHA-1 digest."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def update_csv(path: Path, name_column: str, id_column: str, length: int) -> tuple[int, int]:
    """Update CSV in place and return (processed_rows, added_ids)."""
    if length <= 0:
        raise ValueError("ID length must be > 0")

    newline = detect_newline(path)
    row_count = 0
    added_count = 0

    with path.open("r", encoding="utf-8", newline="") as src:
        reader = csv.DictReader(src, delimiter=";", quotechar='"')
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        if name_column not in reader.fieldnames:
            raise KeyError(f"Column not found: {name_column}")

        has_id_column = id_column in reader.fieldnames
        fieldnames = [f for f in reader.fieldnames if f != id_column] + [id_column]

        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            delete=False,
        ) as dst:
            tmp_path = Path(dst.name)
            writer = csv.DictWriter(
                dst,
                fieldnames=fieldnames,
                delimiter=";",
                quotechar='"',
                lineterminator=newline,
            )
            writer.writeheader()

            for row in reader:
                existing_id = row.get(id_column)
                has_existing_value = (
                    has_id_column
                    and existing_id is not None
                    and str(existing_id).strip() != ""
                )
                if not has_existing_value:
                    name = row.get(name_column, "")
                    if name is None:
                        name = ""
                    row[id_column] = short_sha1(str(name), length=length)
                    added_count += 1
                writer.writerow({key: row.get(key, "") for key in fieldnames})
                row_count += 1

    tmp_path.replace(path)
    return row_count, added_count


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Add an ID column as SHA-1(name) prefix, filling only missing IDs.",
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default="Ice-Cream-Recipes.csv",
        help="Path to the CSV file (default: Ice-Cream-Recipes.csv)",
    )
    parser.add_argument(
        "--name-column",
        default="Ingredients",
        help="Source column for hashing (default: Ingredients)",
    )
    parser.add_argument(
        "--id-column",
        default="ID",
        help="Target ID column name (default: ID)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=7,
        help="Number of SHA-1 hex chars (default: 7)",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entrypoint."""
    args = parse_args()
    path = Path(args.csv_file)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    rows, added = update_csv(
        path=path,
        name_column=args.name_column,
        id_column=args.id_column,
        length=args.length,
    )
    print(f"Processed {rows} rows in {path}; added {added} missing IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
