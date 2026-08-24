r"""Contain the xy rendering backend.

Importing this module registers the xy backend if and only if xy is
installed. It is safe to import even if xy is not installed: the module
simply does not register the backend in that case.
"""

from __future__ import annotations

__all__: list[str] = []

from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from plotmux.backends.registry import register_backend
    from plotmux.backends.xy.backend import XyBackend

    register_backend(XyBackend())
    __all__ += ["XyBackend"]
