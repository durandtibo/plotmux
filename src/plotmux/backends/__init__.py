r"""Contain the backend abstraction used to render chart specs."""

from __future__ import annotations

__all__ = [
    "Backend",
    "BackendCapabilities",
    "available_backends",
    "capabilities",
    "get_backend",
    "register_backend",
]

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.registry import (
    available_backends,
    capabilities,
    get_backend,
    register_backend,
)
