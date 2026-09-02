r"""Helpers to detect and validate the optional plotting backend
dependencies (``altair``, ``bokeh``, ``matplotlib``, ``plotly``,
``xy``).

For each backend, this package re-exports:

- ``is_<backend>_available``: indicate if the package is installed.
- ``check_<backend>``: raise a ``RuntimeError`` if the package is not
  installed.
- ``raise_<backend>_missing_error``: raise a ``RuntimeError`` with a
  message about the missing package.
- ``<backend>_available``: a decorator to conditionally execute a
  function only if the package is installed.
"""

from __future__ import annotations

__all__ = [
    "altair_available",
    "bokeh_available",
    "check_altair",
    "check_bokeh",
    "check_matplotlib",
    "check_plotly",
    "check_xy",
    "is_altair_available",
    "is_bokeh_available",
    "is_matplotlib_available",
    "is_plotly_available",
    "is_xy_available",
    "matplotlib_available",
    "plotly_available",
    "raise_altair_missing_error",
    "raise_bokeh_missing_error",
    "raise_matplotlib_missing_error",
    "raise_plotly_missing_error",
    "raise_xy_missing_error",
    "xy_available",
]

from plotmux.utils.imports.altair import (
    altair_available,
    check_altair,
    is_altair_available,
    raise_altair_missing_error,
)
from plotmux.utils.imports.bokeh import (
    bokeh_available,
    check_bokeh,
    is_bokeh_available,
    raise_bokeh_missing_error,
)
from plotmux.utils.imports.matplotlib import (
    check_matplotlib,
    is_matplotlib_available,
    matplotlib_available,
    raise_matplotlib_missing_error,
)
from plotmux.utils.imports.plotly import (
    check_plotly,
    is_plotly_available,
    plotly_available,
    raise_plotly_missing_error,
)
from plotmux.utils.imports.xy import (
    check_xy,
    is_xy_available,
    raise_xy_missing_error,
    xy_available,
)
