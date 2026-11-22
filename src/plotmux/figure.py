r"""Contain the ``Figure`` wrapper returned by the public API."""

from __future__ import annotations

__all__ = ["Figure"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from plotmux.backends.registry import get_backend
from plotmux.export import save
from plotmux.specs import GridSpec

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

    from plotmux.specs import FigureSpec


@dataclass(slots=True)
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

    spec: FigureSpec
    backend_name: str
    native: Any

    def show(self) -> None:
        r"""Display the figure using the backend's default viewer.

        Raises:
            NotImplementedError: if the backend does not support
                ``show`` (see ``Backend.show``).
        """
        get_backend(self.backend_name).show(self.native)

    @property
    def supported_formats(self) -> frozenset[str]:
        r"""The export formats accepted by ``save`` for this figure.

        Different backends support different export formats (e.g. the
        ``bokeh`` backend only supports ``"html"``, since static image
        export requires an extra, environment-specific dependency), and
        a grid may support fewer formats than a single panel (``xy``
        exports a grid to HTML only). This lets callers check what is
        supported ahead of time instead of discovering it via an
        ``UnsupportedFormatError`` from ``save``.

        Returns:
            The set of export formats accepted by ``save``.
        """
        capabilities = get_backend(self.backend_name).capabilities()
        return (
            capabilities.grid_formats if isinstance(self.spec, GridSpec) else capabilities.formats
        )

    def save(self, path: str | Path) -> None:
        r"""Save the figure to a file.

        The export format is inferred from the file suffix (e.g.
        ``.png``, ``.svg``).

        Args:
            path: The path where to save the figure.

        Raises:
            ValueError: if ``path`` has no suffix, so the export
                format cannot be inferred.
        """
        save(self, path)

    def _repr_mimebundle_(
        self,
        include: Collection[str] | None = None,
        exclude: Collection[str] | None = None,
    ) -> dict[str, Any] | None:
        r"""Return the rich display representation for Jupyter.

        Jupyter calls this method to display a ``Figure`` as the last
        expression of a cell. The representation comes from
        ``Backend.mimebundle`` of the backend that rendered the figure.

        Args:
            include: If given, only the mime types in it are kept.
            exclude: If given, the mime types in it are removed.

        Returns:
            A ``{mime type: data}`` dict, or ``None`` if the native
                object has no rich representation.
        """
        bundle = get_backend(self.backend_name).mimebundle(self.native)
        if bundle is None:
            return None
        return {
            mime_type: data
            for mime_type, data in bundle.items()
            if (include is None or mime_type in include)
            and (exclude is None or mime_type not in exclude)
        }

    def to_native(self) -> Any:
        r"""Return the backend's native figure object.

        This is the escape hatch to reach backend-specific
        functionality that is not exposed by the unified API.

        Returns:
            The backend's native figure object.
        """
        return self.native
