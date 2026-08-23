r"""Top-level package for ``plotmux``."""

from __future__ import annotations

__all__ = ["__version__", "backend", "hist", "set_backend"]

from importlib.metadata import PackageNotFoundError, version

from plotmux.api import hist

# Import backend subpackages for their side effect of registering
# themselves in plotmux.backends.registry, if their underlying
# plotting library is installed.
from plotmux.backends import matplotlib as _matplotlib_backend  # noqa: F401
from plotmux.config import backend, set_backend

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed, fallback if needed
    __version__ = "0.0.0"
