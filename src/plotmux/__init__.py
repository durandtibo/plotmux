r"""Top-level package for ``plotmux``."""

from __future__ import annotations

__all__ = [
    "__version__",
    "backend",
    "bar",
    "cdf",
    "grid",
    "hist",
    "layer",
    "line",
    "scatter",
    "set_backend",
    "slope",
    "stacked_bar",
]

from importlib.metadata import PackageNotFoundError, version

from plotmux.api import bar, cdf, grid, hist, layer, line, scatter, slope, stacked_bar

# No backend is imported here: the registry (plotmux.backends.registry) imports
# the module of a backend, built-in or plugged in through the "plotmux.backends"
# entry-point group, the first time its name is requested.
from plotmux.config import backend, set_backend

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
