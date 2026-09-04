r"""Contain the backend abstraction used to render chart specs."""

from __future__ import annotations

__all__ = ["Backend", "BackendCapabilities", "capabilities", "get_backend", "register_backend"]

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.registry import capabilities, get_backend, register_backend
