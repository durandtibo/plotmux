r"""Helpers to detect and validate the optional backend dependencies
(``altair``, ``bokeh``, ``matplotlib``, ``plotly``, ``xy``).

For each backend, this package provides:

- ``is_<backend>_available``: indicate if the package can be imported.
- ``check_<backend>``: raise a ``MissingPackageError`` if the package
  cannot be imported.

The generic helpers of ``coola.utils.imports`` are re-exported.
"""

from __future__ import annotations

__all__ = [
    "MissingPackageError",
    "availability_cache",
    "check_altair",
    "check_bokeh",
    "check_matplotlib",
    "check_package",
    "check_plotly",
    "check_xy",
    "clear_availability_caches",
    "is_altair_available",
    "is_bokeh_available",
    "is_matplotlib_available",
    "is_plotly_available",
    "is_xy_available",
    "module_available",
    "package_available",
    "raise_package_missing_error",
]

from coola.utils.imports import (
    MissingPackageError,
    availability_cache,
    check_package,
    clear_availability_caches,
    module_available,
    package_available,
    raise_package_missing_error,
)

from plotmux.utils.imports.optional import (
    check_altair,
    check_bokeh,
    check_matplotlib,
    check_plotly,
    check_xy,
    is_altair_available,
    is_bokeh_available,
    is_matplotlib_available,
    is_plotly_available,
    is_xy_available,
)
