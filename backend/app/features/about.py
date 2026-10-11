"""Application metadata shown in the admin About tab."""

import tomllib
from functools import cache
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


@cache
def backend_version() -> str:
    """Version declared in ``backend/pyproject.toml`` (bumped by ``scripts/release.sh``)."""
    try:
        return tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return "unknown"
