r"""Top-level package for ``plotmux``."""

from __future__ import annotations

__all__ = ["__version__", "backend", "grid", "hist", "layer", "line", "scatter", "set_backend"]

from importlib.metadata import PackageNotFoundError, version

from plotmux.api import grid, hist, layer, line, scatter

# Import backend subpackages for their side effect of registering
# themselves in plotmux.backends.registry, if their underlying
# plotting library is installed.
from plotmux.backends import altair as _altair_backend  # noqa: F401
from plotmux.backends import bokeh as _bokeh_backend  # noqa: F401
from plotmux.backends import matplotlib as _matplotlib_backend  # noqa: F401
from plotmux.backends import xy as _xy_backend  # noqa: F401
from plotmux.backends.registry import load_entry_point_backends
from plotmux.config import backend, set_backend

# Register any third-party backend plugged in via the "plotmux.backends"
# entry-point group (see load_entry_point_backends). This runs after the
# two built-in backends above so a plugin can freely reuse those names'
# absence/presence, but never runs before them.
load_entry_point_backends()

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
