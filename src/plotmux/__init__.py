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
]

from importlib.metadata import PackageNotFoundError, version

from plotmux.api import bar, cdf, grid, hist, layer, line, scatter

# The four built-in backend submodules (plotmux.backends.{altair,bokeh,
# matplotlib,xy}) are *not* imported here. Each one eagerly imports its
# underlying plotting library as a side effect of registering itself (see
# e.g. plotmux.backends.matplotlib), so importing all four unconditionally
# would pay that cost for every library that happens to be installed, even
# if only one backend is ever used. Instead, plotmux.backends.registry.
# get_backend imports the matching submodule lazily, the first time that
# backend's name is actually requested.
from plotmux.backends.registry import load_entry_point_backends
from plotmux.config import backend, set_backend

# Register any third-party backend plugged in via the "plotmux.backends"
# entry-point group (see load_entry_point_backends), so a plugin backend is
# discovered before any built-in one has necessarily registered itself
# (none have, at this point: see the comment above), rather than needing
# its own eager-import special case.
load_entry_point_backends()

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
