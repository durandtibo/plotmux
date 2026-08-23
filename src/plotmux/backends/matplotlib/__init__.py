r"""Contain the matplotlib rendering backend.

Importing this module registers the matplotlib backend if and only if
matplotlib is installed. It is safe to import even if matplotlib is not
installed: the module simply does not register the backend in that case.
"""

from __future__ import annotations

__all__: list[str] = []

from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    from plotmux.backends.matplotlib.backend import MatplotlibBackend
    from plotmux.backends.registry import register_backend

    register_backend(MatplotlibBackend())
    __all__ += ["MatplotlibBackend"]
