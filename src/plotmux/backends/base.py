r"""Contain the ``Backend`` base class implemented by rendering
backends."""

from __future__ import annotations

__all__ = ["Backend"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.specs import BaseSpec


class Backend(ABC):
    r"""Define the interface implemented by a rendering backend.

    A backend turns a backend-agnostic ``BaseSpec`` into its native
    figure object (e.g. a matplotlib ``Figure``) and knows how to export
    that native object to a file.
    """

    name: ClassVar[str]

    @abstractmethod
    def render(self, spec: BaseSpec, **kwargs: Any) -> Any:
        r"""Render a spec into the backend's native figure object.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The backend's native figure object.
        """

    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None:
        r"""Export a native figure object to a file.

        Args:
            native: The native figure object, as returned by
                ``render``.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).
        """
