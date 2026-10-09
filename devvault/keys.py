"""Public API for reading and managing DevVault values."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, os.PathLike[str]]
_CONFIG_DIR = Path.home() / ".devvault"
_CONFIG_FILE = _CONFIG_DIR / "config.json"
_DEFAULT_DIR = _CONFIG_DIR
_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def _read_config() -> dict:
    try:
        with _CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict) and isinstance(data.get("directory"), str):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"directory": str(_DEFAULT_DIR)}


def _current_dir() -> Path:
    data = _read_config()
    directory = Path(data["directory"]).expanduser()
    return directory.resolve()


def _write_config(directory: Path) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = _CONFIG_FILE.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump({"directory": str(directory.resolve())}, file, ensure_ascii=False, indent=2)
        file.write("\n")
    temporary.replace(_CONFIG_FILE)


def dir(path: Optional[PathLike] = None) -> str:
    """Get the vault directory, or set it with dir('PATH').

    The returned path is the directory containing .env, not the .env file itself.
    Calling dir(path) saves the setting for future CLI and Python sessions.
    """
    if path is not None:
        target = Path(path).expanduser()
        if not target.is_absolute():
            target = Path.cwd() / target
        target = target.resolve()
        target.mkdir(parents=True, exist_ok=True)
        _write_config(target)
        return str(target)

    return str(_current_dir())


def _env_file() -> Path:
    directory = _current_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / ".env"


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _KEY_PATTERN.fullmatch(name):
        raise ValueError(
            "Nom de clé invalide. Utilise des lettres, chiffres, '.', '_' ou '-', "
            "et commence par une lettre ou '_'."
        )
    return name


def _read_all() -> dict[str, str]:
    path = _env_file()
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return values

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if not _KEY_PATTERN.fullmatch(name):
            continue
        raw_value = raw_value.strip()
        if raw_value.startswith('"'):
            try:
                decoded = json.loads(raw_value)
                if isinstance(decoded, str):
                    values[name] = decoded
                    continue
            except json.JSONDecodeError:
                pass
        values[name] = raw_value
    return values


def _write_all(values: dict[str, str]) -> None:
    path = _env_file()
    temporary = path.with_suffix(".env.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as file:
        file.write("# DevVault local vault. Keep this file private.\n")
        for name in sorted(values):
            file.write(f"{name}={json.dumps(values[name], ensure_ascii=False)}\n")
    temporary.replace(path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        # Windows may not support POSIX-style permissions; the vault still works.
        pass


def add(name: str, value: str) -> None:
    """Create or replace a key."""
    name = _validate_name(name)
    if not isinstance(value, str):
        value = str(value)
    values = _read_all()
    values[name] = value
    _write_all(values)


def get(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return a key's value, or default (None by default) if it is missing."""
    name = _validate_name(name)
    return _read_all().get(name, default)


def remove(name: str) -> bool:
    """Delete a key. Return True if it existed, otherwise False."""
    name = _validate_name(name)
    values = _read_all()
    if name not in values:
        return False
    del values[name]
    _write_all(values)
    return True


def list_keys() -> list[str]:
    """Return key names only; values are never included."""
    return sorted(_read_all().keys())
