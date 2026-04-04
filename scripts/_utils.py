"""Shared helpers for small CLI scripts in this repository."""

from __future__ import annotations

import sys
import shlex
from pathlib import Path
from datetime import datetime
from collections.abc import Callable

import yaml

from appdirs import user_config_dir


APP_NAME = "ice-creamery"
APP_AUTHOR = "jhermann"
SUPPORTED_SUFFIXES = {".ods"}  # we do not read .fods files by default
DEFAULT_CONFIG_NAME = "config.yml"
DEFAULT_CONFIG = {
    "sheet_directory": ".",
    "sheet_recursive": False,
    "extensions": sorted(SUPPORTED_SUFFIXES),
    "libreoffice_cmd": ["libreoffice"],
    "path_mapper": [],
    "open_args": ["--calc", "{open_path}"],
}

__all__ = [
    "SUPPORTED_SUFFIXES",
    "DEFAULT_CONFIG",
    "get_default_config_path",
    "normalize_extensions",
    "load_yaml_config",
    "create_yaml_config_file",
]


def get_default_config_path(config_name: str = DEFAULT_CONFIG_NAME) -> Path:
    """Return the default config path in the user config directory."""
    return Path(user_config_dir(APP_NAME, APP_AUTHOR)) / config_name


def normalize_extensions(values: list[str] | None, defaults: set[str]) -> set[str]:
    """Normalize file extension values and fall back to defaults when empty."""
    if not values:
        return set(defaults)

    normalized = set()
    for value in values:
        suffix = str(value).strip().lower()
        if not suffix:
            continue
        if not suffix.startswith("."):
            suffix = f".{suffix}"
        normalized.add(suffix)
    return normalized or set(defaults)


def normalize_command(value: str | list[str], default: list[str] | None = None) -> list[str]:
    """Normalize command input into a list of non-empty string tokens."""
    if isinstance(value, str):
        command = shlex.split(value)
    elif isinstance(value, list):
        command = [str(item) for item in value if str(item).strip()]
    else:
        command = []

    if command:
        return command
    return list(default or [])


def load_yaml_config(
    config_path: Path,
    *,
    normalize: dict[str, Callable] | None = None,
) -> dict:
    """Load YAML config and optionally normalize selected keys."""
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping: {config_path}")

    if not normalize:
        return data

    config = {}
    for key, value in data.items():
        if value is None:
            continue
        handler = normalize.get(key)
        config[key] = handler(value) if handler else value
    return config


def create_yaml_config_file(config_path: Path, default_config: dict) -> None:
    """Create a YAML config file or write it to stdout for '-' paths."""
    if config_path == Path("-"):
        sys.stdout.write("# This is a config file for the ice-creamery scripts.\n")
        sys.stdout.write("# You can customize the settings here or use CLI arguments to override them.\n")
        sys.stdout.write(f"# Created at {datetime.now().isoformat(timespec='seconds', sep=' ')}.\n\n")
        yaml.safe_dump(default_config, sys.stdout, sort_keys=False)
        return

    if config_path.exists():
        raise FileExistsError(f"⛔ Config file already exists: {config_path}")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as handle:
        handle.write("# This is a config file for the ice-creamery scripts.\n")
        handle.write("# You can customize the settings here or use CLI arguments to override them.\n")
        handle.write(f"# Created at {datetime.now().isoformat(timespec='seconds', sep=' ')}.\n\n")
        yaml.safe_dump(default_config, handle, sort_keys=False)
