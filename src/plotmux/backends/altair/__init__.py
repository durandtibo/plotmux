r"""Contain the altair rendering backend.

Importing this module registers the altair backend if and only if altair
is installed. It is safe to import even if altair is not installed: the
module simply does not register the backend in that case.
"""

from __future__ import annotations

__all__: list[str] = []

from plotmux.utils.imports import is_altair_available

if is_altair_available():
    from plotmux.backends.altair.backend import AltairBackend
    from plotmux.backends.registry import register_backend

    register_backend(AltairBackend())
    __all__ += ["AltairBackend"]
