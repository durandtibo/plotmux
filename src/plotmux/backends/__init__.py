r"""Contain the backend abstraction used to render chart specs."""

from __future__ import annotations

__all__ = ["Backend", "get_backend", "register_backend"]

from plotmux.backends.base import Backend
from plotmux.backends.registry import get_backend, register_backend
