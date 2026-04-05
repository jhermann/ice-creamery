#! /usr/bin/env python3
""" Utility to handle ice cream recipes written using LibreOffice spreadsheets.

    This script supports these actions:
    * lists sheet names
    * search a glob pattern in sheet names
    * search a glob pattern in sheet names and print the content of the first cell in the
"""

from __future__ import annotations

# isorted imports
import re
import os
import sys
import fnmatch
import argparse
import subprocess
import platform
import xml.etree.ElementTree as ET
import shutil

from pathlib import Path
from zipfile import BadZipFile, ZipFile

import yaml

from pick import pick
from attrdict import AttrDict

# DO NOT TOUCH THIS IMPORT, NO "importlib"!
from _utils import (
    SUPPORTED_SUFFIXES,
    DEFAULT_CONFIG,
    get_default_config_path,
    normalize_command,
    normalize_extensions,
    load_yaml_config,
    create_yaml_config_file,
)

class SpreadSheetSupport:
    """Helpers for reading spreadsheet files and matching sheet names."""

    TABLE_NS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    TABLE_TAG = f"{{{TABLE_NS}}}table"
    TABLE_NAME_ATTR = f"{{{TABLE_NS}}}name"

    @staticmethod
    def iter_spreadsheet_files(sheet_directory: Path, sheet_recursive: bool, suffixes: set[str]):
        iterator = sheet_directory.rglob("*") if sheet_recursive else sheet_directory.iterdir()
        for path in sorted(iterator):
            if not path.is_file():
                continue
            if path.name.startswith(".~lock."):
                continue
            if path.suffix.lower() in suffixes:
                yield path

    @staticmethod
    def list_sheet_names_from_fods(path: Path) -> list[str]:
        tree = ET.parse(path)
        return SpreadSheetSupport.extract_sheet_names(tree.getroot())

    @staticmethod
    def list_sheet_names_from_ods(path: Path) -> list[str]:
        with ZipFile(path) as archive:
            content = archive.read("content.xml")
        root = ET.fromstring(content)
        return SpreadSheetSupport.extract_sheet_names(root)

    @staticmethod
    def extract_sheet_names(root: ET.Element) -> list[str]:
        return [
            table.attrib[SpreadSheetSupport.TABLE_NAME_ATTR]
            for table in root.iterfind(f".//{SpreadSheetSupport.TABLE_TAG}")
            if SpreadSheetSupport.TABLE_NAME_ATTR in table.attrib
        ]

    @staticmethod
    def list_sheet_names(path: Path) -> list[str]:
        suffix = path.suffix.lower()
        if suffix == ".fods":
            return SpreadSheetSupport.list_sheet_names_from_fods(path)
        if suffix == ".ods":
            return SpreadSheetSupport.list_sheet_names_from_ods(path)
        raise ValueError(f"Unsupported file type: {path}")

    @staticmethod
    def compile_search_pattern(pattern: str) -> re.Pattern:
        if pattern.startswith("/"):
            regex = pattern[1:]
            if regex.endswith("/"):
                regex = regex[:-1]
            return re.compile(regex, re.IGNORECASE)

        return re.compile(fnmatch.translate(f"*{pattern}*"), re.IGNORECASE)

    @staticmethod
    def match_sheet_names(sheet_names: list[str], patterns: list[str]) -> list[str]:
        search_patterns = [SpreadSheetSupport.compile_search_pattern(pattern) for pattern in patterns]
        return [
            sheet_name
            for sheet_name in sheet_names
            if any(pattern.search(sheet_name) for pattern in search_patterns)
        ]

    @staticmethod
    def display_path(path: Path, sheet_directory: Path, abspath: bool = False) -> Path | str:
        if abspath:
            return path.resolve()
        try:
            return path.relative_to(sheet_directory)
        except ValueError:
            return path.name

    @staticmethod
    def format_sheet_label(sheet_name: str, position: int, width: int) -> str:
        return f"[#{position:0{width}d}] {sheet_name}"

    @staticmethod
    def map_open_path(path: Path, path_mapper_cmd: list[str]) -> str:
        if not path_mapper_cmd:
            return str(path)

        mapped_path = subprocess.check_output([*path_mapper_cmd, str(path)], encoding="utf-8")
        mapped_path = mapped_path.strip()
        if not mapped_path:
            raise ValueError("Path mapper returned an empty path")
        return mapped_path

    @staticmethod
    def open_sheet_match(match: AttrDict, libreoffice_cmd: list[str],
                         path_mapper_cmd: list[str], open_args: list[str] | None = None, verbose: bool = False) -> None:
        open_path = SpreadSheetSupport.map_open_path(match.path, path_mapper_cmd)
        namespace = {"open_path": open_path, "sheet_name": match.sheet_name}
        formatted_args = [arg.format(**namespace) for arg in (open_args or [])]
        command = [*libreoffice_cmd, *formatted_args, open_path]
        if verbose:
            print(f"⛭ command: {' '.join(command)}")
        popen_kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }

        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["start_new_session"] = True

        subprocess.Popen(command, **popen_kwargs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__.split('.')[0] + '.',
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["list", "search", "s", "open", "o", "info", "i", "fix-id"],
        default="list",
        help="Action to run. Supported: list, search (or s), open (or o), info (or i), fix-id.",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Optional arguments for the selected action.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Directory containing .ods files.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan subdirectories recursively.",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        help="File extensions to include, for example: ods fods.",
    )
    parser.add_argument(
        "-a",
        "--abspath",
        action="store_true",
        help="Display spreadsheet file paths as absolute paths.",
    )
    parser.add_argument(
        "-m",
        "--mapped",
        action="store_true",
        help="Display spreadsheet file paths mapped through the configured path_mapper command.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help=f"Path to a YAML config file. Use '-' with --create-config to write to stdout."
             f" Default: {get_default_config_path()}",
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a config file with default values and exit.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict:
    return load_yaml_config(
        config_path,
        normalize={
            "sheet_directory": lambda value: Path(value).expanduser(),
            "sheet_recursive": bool,
            "extensions": lambda value: normalize_extensions(value, SUPPORTED_SUFFIXES),
            "libreoffice_cmd": lambda value: normalize_command(value, DEFAULT_CONFIG["libreoffice_cmd"]),
            "path_mapper": lambda value: normalize_command(value, DEFAULT_CONFIG["path_mapper"]),
            "open_args": lambda value: normalize_command(value, DEFAULT_CONFIG["open_args"]),
        },
    )


def create_config_file(config_path: Path) -> None:
    create_yaml_config_file(config_path, DEFAULT_CONFIG)


def normalize_patterns(patterns: list[str]) -> list[str]:
    cwd_basename = Path.cwd().resolve().name or str(Path.cwd().resolve())
    return [cwd_basename.replace(' (Deluxe)', '') if pattern == "." else pattern
            for pattern in patterns]


def resolve_settings(args: argparse.Namespace) -> AttrDict:
    config_path = args.config.expanduser() if args.config else get_default_config_path()
    config = load_config(config_path)
    action = {"s": "search", "o": "open", "i": "info"}.get(args.action, args.action)

    sheet_directory = args.directory
    if sheet_directory is None:
        sheet_directory = config.get("sheet_directory", config.get("directory"))
    if sheet_directory is None:
        raise ValueError("A directory is required via CLI or config file")

    sheet_recursive = args.recursive or config.get(
        "sheet_recursive",
        config.get("recursive", DEFAULT_CONFIG["sheet_recursive"]),
    )
    extensions = normalize_extensions(args.extensions, SUPPORTED_SUFFIXES) if args.extensions else config.get(
        "extensions",
        set(DEFAULT_CONFIG["extensions"]),
    )

    return AttrDict(
        config_path=config_path,
        action=action,
        sheet_directory=Path(sheet_directory).expanduser(),
        sheet_recursive=sheet_recursive,
        extensions=extensions,
        libreoffice_cmd=config.get("libreoffice_cmd", DEFAULT_CONFIG["libreoffice_cmd"]),
        path_mapper=config.get("path_mapper", DEFAULT_CONFIG["path_mapper"]),
        open_args=config.get("open_args", DEFAULT_CONFIG["open_args"]),
        abspath=args.abspath,
        mapped=args.mapped,
        verbose=args.verbose,
        patterns=normalize_patterns(args.args) if action in {"search", "open"} else args.args,
    )


def print_info(settings: AttrDict) -> None:
    libreoffice_bin = settings.libreoffice_cmd[0] if settings.libreoffice_cmd else ""
    bold = "\033[1m"
    reset = "\033[0m"
    label_width = 3 * 8

    def info(label: str, value) -> None:
        print(f"{bold}{label.ljust(label_width)}{reset} {value}")

    def bool_marker(value: bool) -> str:
        return "☑️" if value else "⛔"

    def with_exists_marker(value, exists: bool | None = None) -> str:
        if exists is None:
            exists = bool(value.exists())
        marker = "✅" if exists else "❌"
        return f"{marker} {value}"

    info("Config Path:", with_exists_marker(settings.config_path))

    libreoffice_found = bool(shutil.which(libreoffice_bin))
    libreoffice_call = (
        settings.libreoffice_cmd + ('\\\n     ' + ' ' * label_width,)
        + settings.open_args)
    info("LibreOffice Command:",
         with_exists_marker(" ".join(libreoffice_call), libreoffice_found))
    info("Path Mapper:", " ".join(settings.path_mapper) or "(none)")

    info("Sheet Directory:", with_exists_marker(settings.sheet_directory))
    info("Sheet Recursive:", bool_marker(settings.sheet_recursive))
    info("Extensions:", ", ".join(sorted(settings.extensions)))
    info("Python:", f'{sys.executable} {platform.python_version()}')
    info("Platform:", platform.platform())
    info("Script File:", Path(__file__).resolve())
    info("Current Working Dir:", Path.cwd())


def main() -> int:
    args = parse_args()

    # Handle fix-id action early - it doesn't need config or sheet directory
    if args.action == "fix-id":
        try:
            from _fix_ids import main as fix_ids_main
            return fix_ids_main(args.args)
        except ImportError as exc:
            print(f"⚡ Failed to load _fix_ids module: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"⚡ fix-id action failed: {exc}", file=sys.stderr)
            return 2
        return 1  # some other error not caught

    try:
        config_path = args.config.expanduser() if args.config else get_default_config_path()
        if args.create_config:
            create_config_file(config_path)
            if config_path != Path("-"):
                print(f"🆕 Created config file at {config_path}")
            return 0

        settings = resolve_settings(args)
    except (FileExistsError, OSError, ValueError, yaml.YAMLError) as exc:
        print(exc, file=sys.stderr)
        return 2

    if settings.action not in {"list", "search", "open", "info"}:
        print(f"⚡ Unsupported action: {settings.action}", file=sys.stderr)
        return 2

    if settings.action == "info":
        print_info(settings)
        return 0

    if settings.action in {"search", "open"} and not settings.patterns:
        print(f"⁉️ Action '{settings.action}' requires at least one glob pattern", file=sys.stderr)
        return 2

    if not settings.sheet_directory.is_dir():
        print(f"⚡ Not a directory: {settings.sheet_directory}", file=sys.stderr)
        return 2

    spreadsheet_files = list(SpreadSheetSupport.iter_spreadsheet_files(
        settings.sheet_directory,
        settings.sheet_recursive,
        settings.extensions,
    ))
    if not spreadsheet_files:
        print(f"⚡ No LibreOffice spreadsheet files found in {settings.sheet_directory}", file=sys.stderr)
        return 1

    had_errors = False
    had_matches = False
    sheet_matches = []

    for path in spreadsheet_files:
        try:
            all_sheet_names = SpreadSheetSupport.list_sheet_names(path)
        except (ET.ParseError, BadZipFile, KeyError, OSError) as exc:
            had_errors = True
            print(f"{path}: ERROR: {exc}", file=sys.stderr)
            continue

        indexed_sheet_names = list(enumerate(all_sheet_names, start=1))
        position_width = max(2, len(str(len(all_sheet_names))))

        if settings.action in {"search", "open"}:
            search_patterns = [SpreadSheetSupport.compile_search_pattern(pattern) for pattern in settings.patterns]
            indexed_sheet_names = [
                (position, sheet_name)
                for position, sheet_name in indexed_sheet_names
                if any(pattern.search(sheet_name) for pattern in search_patterns)
            ]
            if not indexed_sheet_names:
                continue
            had_matches = True

        if settings.mapped:
            try:
                display_path = SpreadSheetSupport.map_open_path(path, settings.path_mapper)
            except (subprocess.CalledProcessError, FileNotFoundError, OSError, ValueError) as exc:
                had_errors = True
                print(f"⚡ {path}: ERROR: path mapping failed: {exc}", file=sys.stderr)
                continue
        else:
            display_path = SpreadSheetSupport.display_path(path, settings.sheet_directory, settings.abspath)

        if settings.action == "open":
            for position, sheet_name in indexed_sheet_names:
                sheet_matches.append(AttrDict(
                    path=path,
                    display_path=display_path,
                    sheet_name=sheet_name,
                    sheet_position=position,
                    sheet_position_width=position_width,
                ))
            continue

        print(display_path)
        for position, sheet_name in indexed_sheet_names:
            label = SpreadSheetSupport.format_sheet_label(sheet_name, position, position_width)
            print(f"  - {label}")

    if settings.action == "open":
        if not sheet_matches and not had_errors:
            return 1

        if len(sheet_matches) == 1:
            selected_match = sheet_matches[0]
        else:
            options = [
                (
                    f"{match.display_path} :: "
                    f"{SpreadSheetSupport.format_sheet_label(match.sheet_name, match.sheet_position, match.sheet_position_width)}"
                )
                for match in sheet_matches
            ]
            try:
                _, selected_index = pick(options, title="Select a sheet to open")
            except (KeyboardInterrupt, EOFError):
                print("Selection cancelled.", file=sys.stderr)
                return 1
            selected_match = sheet_matches[selected_index]

        selected_label = SpreadSheetSupport.format_sheet_label(
            selected_match.sheet_name,
            selected_match.sheet_position,
            selected_match.sheet_position_width,
        )
        print(f"Opening {selected_match.display_path} :: {selected_label}")
        SpreadSheetSupport.open_sheet_match(
            selected_match,
            settings.libreoffice_cmd,
            settings.path_mapper,
            settings.open_args,
            settings.verbose,
        )
        return 1 if had_errors else 0

    if settings.action == "search" and not had_matches and not had_errors:
        return 1

    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
