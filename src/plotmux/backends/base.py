r"""Contain the ``Backend`` base class implemented by rendering
backends, and the capabilities a backend declares.

A backend draws the three primitives of a scene (see
``plotmux.scene``) and applies the axes style: it owns no decision
that changes the numbers on the screen.
"""

from __future__ import annotations

__all__ = ["Backend", "BackendCapabilities"]

import dataclasses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from plotmux.exceptions import UnsupportedFormatError, UnsupportedSpecError
from plotmux.primitives import Points
from plotmux.scene import AxesScene, GridScene, build_scene

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.specs import FigureSpec

# The rich-display methods a native figure may define, by mime type.
_REPR_METHODS = {
    "text/html": "_repr_html_",
    "image/svg+xml": "_repr_svg_",
    "image/png": "_repr_png_",
    "image/jpeg": "_repr_jpeg_",
}


@dataclasses.dataclass(frozen=True, slots=True)
class BackendCapabilities:
    r"""Declare what a backend supports, as data.

    The base class checks a scene against it before any drawing (see
    ``Backend.render``) and ``plotmux.export.save`` checks the format
    of a file against it before any file or directory is created, so a
    request a backend cannot honor is an error, not a silent no-op.

    Args:
        name: The name of the backend (e.g. ``"matplotlib"``).
        formats: The export formats of a single-panel figure.
        grid_formats: The export formats of a grid. It differs from
            ``formats`` when the library cannot compose the panels
            (``xy`` exports a grid to HTML only).
        legend_locations: The legend locations the backend honors.
        markers: The scatter markers the backend draws.

    Example:
        ```pycon
        >>> from plotmux.backends.base import BackendCapabilities
        >>> caps = BackendCapabilities(
        ...     name="demo",
        ...     formats=frozenset({"png"}),
        ...     grid_formats=frozenset({"png"}),
        ...     legend_locations=frozenset({"top"}),
        ...     markers=frozenset({"circle"}),
        ... )
        >>> caps.check_format("png")

        ```
    """

    name: str
    formats: frozenset[str]
    grid_formats: frozenset[str]
    legend_locations: frozenset[str]
    markers: frozenset[str]

    def check(self, scene: AxesScene | GridScene) -> None:
        r"""Check that a scene only asks for what the backend supports.

        Args:
            scene: The scene to check.

        Raises:
            UnsupportedSpecError: if a legend location or a marker is
                not supported. The message names the backend and the
                supported values. Also a ``NotImplementedError``.

        Example:
            ```pycon
            >>> from plotmux.backends.base import BackendCapabilities
            >>> from plotmux.scene import AxesScene
            >>> caps = BackendCapabilities("demo", frozenset(), frozenset(), frozenset(), frozenset())
            >>> caps.check(AxesScene(primitives=()))

            ```
        """
        panels = scene.panels if isinstance(scene, GridScene) else (scene,)
        for panel in panels:
            location = panel.legend.location if panel.legend is not None else None
            if location is not None and location not in self.legend_locations:
                msg = (
                    f"The {self.name} backend does not support legend_location={location!r}: "
                    f"supported values are {sorted(self.legend_locations)}"
                )
                raise UnsupportedSpecError(msg)
            for primitive in panel.primitives:
                if (
                    isinstance(primitive, Points)
                    and primitive.marker is not None
                    and primitive.marker not in self.markers
                ):
                    msg = (
                        f"The {self.name} backend does not support marker={primitive.marker!r}: "
                        f"supported values are {sorted(self.markers)}"
                    )
                    raise UnsupportedSpecError(msg)

    def check_format(self, fmt: str, *, grid: bool = False) -> None:
        r"""Check that an export format is supported.

        Args:
            fmt: The export format (e.g. ``"png"``).
            grid: ``True`` for the figure of a grid.

        Raises:
            UnsupportedFormatError: if ``fmt`` is not supported. The
                message names the backend and the supported formats.
                Also a ``ValueError``.

        Example:
            ```pycon
            >>> from plotmux.backends.base import BackendCapabilities
            >>> caps = BackendCapabilities("demo", frozenset({"png"}), frozenset(), frozenset(), frozenset())
            >>> caps.check_format("png")
            >>> caps.check_format("png", grid=True)
            Traceback (most recent call last):
                ...
            plotmux.exceptions.UnsupportedFormatError: The demo backend does not support exporting a grid to 'png': supported formats are []

            ```
        """
        supported = self.grid_formats if grid else self.formats
        if fmt not in supported:
            kind = "a grid" if grid else "a figure"
            msg = (
                f"The {self.name} backend does not support exporting {kind} to {fmt!r}: "
                f"supported formats are {sorted(supported)}"
            )
            raise UnsupportedFormatError(msg)


class Backend(ABC):
    r"""Define the interface implemented by a rendering backend.

    A backend turns a scene (the lowered spec of a figure, see
    ``plotmux.scene.build_scene``) into its native figure object
    (e.g. a matplotlib ``Figure``) and knows how to export that native
    object to a file. A backend implements ``capabilities``, ``draw``
    and ``save``, and ``show`` and ``mimebundle`` where its library
    needs them. ``render`` is not overridden.
    """

    name: ClassVar[str]

    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        r"""Declare the export formats, legend locations and markers
        supported by this backend.

        Returns:
            This backend's ``BackendCapabilities``.
        """

    @abstractmethod
    def draw(self, scene: AxesScene | GridScene) -> Any:
        r"""Draw a scene into the backend's native figure object.

        Args:
            scene: The scene to draw: one axes, or a grid of axes.

        Returns:
            The backend's native figure object.
        """

    def render(self, spec: FigureSpec) -> Any:
        r"""Render a spec into the backend's native figure object.

        The spec is lowered to a scene, checked against
        ``capabilities`` and drawn. The check happens before any
        drawing.

        Args:
            spec: The spec of a panel or of a grid.

        Returns:
            The backend's native figure object.

        Raises:
            UnsupportedSpecError: if the spec asks for something the
                backend does not support (see
                ``BackendCapabilities.check``).
        """
        scene = build_scene(spec)
        self.capabilities().check(scene)
        return self.draw(scene)

    def show(self, native: Any) -> None:
        r"""Display a native figure object with the library's own viewer.

        The default implementation raises. A backend overrides it with
        the way its library displays a figure (a window, a browser tab).

        Args:
            native: The native figure object, as returned by
                ``render``.

        Raises:
            NotImplementedError: if the backend does not support
                ``show``.
        """
        msg = f"The {self.name} backend does not support 'show'"
        raise NotImplementedError(msg)

    def mimebundle(self, native: Any) -> dict[str, Any] | None:
        r"""Return the rich display representation of a native figure.

        Jupyter calls this through ``Figure._repr_mimebundle_`` to
        display a figure as the last expression of a cell. The default
        implementation uses the representation of the native object
        itself: its ``_repr_mimebundle_`` if it has one, else the
        ``_repr_html_``, ``_repr_svg_``, ``_repr_png_`` and
        ``_repr_jpeg_`` methods it defines. A backend overrides it when
        the native object has none of them (e.g. matplotlib).

        Args:
            native: The native figure object, as returned by
                ``render``.

        Returns:
            A ``{mime type: data}`` dict, or ``None`` if the native
                object has no rich representation.
        """
        method = getattr(native, "_repr_mimebundle_", None)
        if method is not None:
            return method()
        bundle: dict[str, Any] = {}
        for mime_type, name in _REPR_METHODS.items():
            method = getattr(native, name, None)
            data = method() if method is not None else None
            if data is not None:
                bundle[mime_type] = data
        return bundle or None

    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None:
        r"""Export a native figure object to a file.

        Args:
            native: The native figure object, as returned by
                ``render``.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).
        """
