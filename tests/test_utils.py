"""Pytest coverage for shared helpers in scripts/_utils.py."""

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def utils(load_script_module):
    """Load the shared utility module from the scripts directory."""
    return load_script_module("_utils.py", "_utils")


def test_get_default_config_path_uses_appdirs_location(mocker, tmp_path, utils):
    """Default config paths should be rooted in the appdirs config directory."""
    # Arrange
    config_dir = tmp_path / "config-home"
    mocker.patch.object(utils, "user_config_dir", return_value=str(config_dir))

    # Act
    result = utils.get_default_config_path()

    # Assert
    assert result == config_dir / utils.DEFAULT_CONFIG_NAME


@pytest.mark.parametrize(
    ("values", "defaults", "expected"),
    [
        (None, {".ods"}, {".ods"}),
        ([], {".ods"}, {".ods"}),
        ([" ods ", "YML", ".CSV", "", "  ", ".csv"], {".ods"}, {".ods", ".yml", ".csv"}),
        (["", "   "], {".ods", ".fods"}, {".ods", ".fods"}),
    ],
)
def test_normalize_extensions_handles_defaults_and_cleanup(utils, values, defaults, expected):
    """Extension normalization should lowercase values, add dots, and fall back to defaults."""
    # Arrange

    # Act
    result = utils.normalize_extensions(values, defaults)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        ("libreoffice --calc file.ods", None, ["libreoffice", "--calc", "file.ods"]),
        (["libreoffice", "", 7, "   ", "--calc"], None, ["libreoffice", "7", "--calc"]),
        (None, ["libreoffice"], ["libreoffice"]),
        ({"bad": "type"}, ["soffice"], ["soffice"]),
    ],
)
def test_normalize_command_supports_strings_lists_and_fallbacks(utils, value, default, expected):
    """Command normalization should split strings, filter list blanks, and use defaults when needed."""
    # Arrange

    # Act
    result = utils.normalize_command(value, default)

    # Assert
    assert result == expected


def test_load_yaml_config_returns_empty_for_missing_file(tmp_path, utils):
    """Missing config files should load as an empty mapping."""
    # Arrange
    config_path = tmp_path / "missing.yml"

    # Act
    result = utils.load_yaml_config(config_path)

    # Assert
    assert result == {}


def test_load_yaml_config_applies_normalizers_and_skips_none(tmp_path, utils):
    """Configured normalizers should transform values while omitting null entries."""
    # Arrange
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "extensions:\n"
        "  - ODS\n"
        "  - csv\n"
        "sheet_recursive: true\n"
        "path_mapper: null\n",
        encoding="utf-8",
    )

    # Act
    result = utils.load_yaml_config(
        config_path,
        normalize={
            "extensions": lambda value: utils.normalize_extensions(value, utils.SUPPORTED_SUFFIXES),
            "sheet_recursive": lambda value: not value,
        },
    )

    # Assert
    assert result == {
        "extensions": {".ods", ".csv"},
        "sheet_recursive": False,
    }


def test_load_yaml_config_rejects_non_mapping_yaml(tmp_path, utils):
    """Config YAML must contain a mapping at the document root."""
    # Arrange
    config_path = tmp_path / "config.yml"
    config_path.write_text("- not\n- a mapping\n", encoding="utf-8")

    # Act / Assert
    with pytest.raises(ValueError, match="must contain a mapping"):
        utils.load_yaml_config(config_path)


def test_create_yaml_config_file_writes_header_and_yaml(mocker, tmp_path, utils):
    """Creating a config file should write the banner and YAML payload to disk."""
    # Arrange
    config_path = tmp_path / "nested" / "config.yml"
    fake_datetime = mocker.patch.object(utils, "datetime")
    fake_datetime.now.return_value.isoformat.return_value = "2026-04-04 10:11:12"

    # Act
    utils.create_yaml_config_file(config_path, {"extensions": [".ods"], "sheet_recursive": False})

    # Assert
    written = config_path.read_text(encoding="utf-8")
    assert "# This is a config file for the ice-creamery scripts." in written
    assert "# Created at 2026-04-04 10:11:12." in written
    assert "extensions:" in written
    assert "- .ods" in written
    assert "sheet_recursive: false" in written


def test_create_yaml_config_file_writes_to_stdout_for_dash_path(mocker, capsys, utils):
    """Using '-' should emit the generated config to stdout instead of creating a file."""
    # Arrange
    fake_datetime = mocker.patch.object(utils, "datetime")
    fake_datetime.now.return_value.isoformat.return_value = "2026-04-04 10:11:12"

    # Act
    utils.create_yaml_config_file(Path("-"), {"extensions": [".ods"]})

    # Assert
    captured = capsys.readouterr()
    assert "# This is a config file for the ice-creamery scripts." in captured.out
    assert "# Created at 2026-04-04 10:11:12." in captured.out
    assert "extensions:" in captured.out
    assert "- .ods" in captured.out


def test_create_yaml_config_file_rejects_existing_file(tmp_path, utils):
    """Existing config files should not be overwritten."""
    # Arrange
    config_path = tmp_path / "config.yml"
    config_path.write_text("already here\n", encoding="utf-8")

    # Act / Assert
    with pytest.raises(FileExistsError, match="already exists"):
        utils.create_yaml_config_file(config_path, {"extensions": [".ods"]})
