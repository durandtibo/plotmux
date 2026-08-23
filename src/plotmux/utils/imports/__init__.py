r"""Helpers to detect, lazily import, and validate optional
dependencies."""

from __future__ import annotations

__all__ = [
    "check_matplotlib",
    "check_xy",
    "is_matplotlib_available",
    "is_xy_available",
    "matplotlib_available",
    "raise_matplotlib_missing_error",
    "raise_xy_missing_error",
    "xy_available",
]

from plotmux.utils.imports.matplotlib import (
    check_matplotlib,
    is_matplotlib_available,
    matplotlib_available,
    raise_matplotlib_missing_error,
)
from plotmux.utils.imports.xy import (
    check_xy,
    is_xy_available,
    raise_xy_missing_error,
    xy_available,
)
