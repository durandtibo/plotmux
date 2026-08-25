r"""Contain the ``Figure`` wrapper returned by the public API."""

from __future__ import annotations

__all__ = ["Figure"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from plotmux.backends.registry import get_backend
from plotmux.export import save

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.specs import BaseSpec


@dataclass
class Figure:
    r"""Wrap the result of rendering a spec through a backend.

    ``Figure`` is the object returned to the user by the public API
    (``plotmux.hist``, ``plotmux.line``, ``plotmux.scatter``, ...).
    It keeps the spec that produced it, the name of the backend that
    rendered it, and the backend's native figure object.

    Args:
        spec: The spec that was rendered.
        backend_name: The name of the backend that rendered
            ``native``.
        native: The backend's native figure object (e.g. a
            matplotlib ``Figure``).
    """

    spec: BaseSpec
    backend_name: str
    native: Any

    def show(self) -> None:
        r"""Display the figure using the backend's default viewer."""
        show = getattr(self.native, "show", None)
        if show is None:
            msg = f"The native object of type {type(self.native)} does not support 'show'"
            raise NotImplementedError(msg)
        show()

    @property
    def supported_formats(self) -> frozenset[str]:
        r"""The export formats accepted by ``save`` for this figure's
        backend.

        Different backends support different export formats (e.g. the
        ``bokeh`` backend only supports ``"html"``, since static image
        export requires an extra, environment-specific dependency).
        This lets callers check what is supported ahead of time
        instead of discovering it via a ``ValueError`` from ``save``.

        Returns:
            The set of export formats accepted by ``save``.
        """
        return get_backend(self.backend_name).supported_formats

    def save(self, path: str | Path) -> None:
        r"""Save the figure to a file.

        The export format is inferred from the file suffix (e.g.
        ``.png``, ``.svg``).

        Args:
            path: The path where to save the figure.
        """
        save(self, path)

    def to_native(self) -> Any:
        r"""Return the backend's native figure object.

        This is the escape hatch to reach backend-specific
        functionality that is not exposed by the unified API.

        Returns:
            The backend's native figure object.
        """
        return self.native
