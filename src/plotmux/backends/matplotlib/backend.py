r"""Contain the matplotlib ``Backend`` implementation.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["MatplotlibBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

import matplotlib.pyplot as plt

from plotmux.backends.base import Backend
from plotmux.backends.matplotlib.histogram import render_histogram
from plotmux.backends.matplotlib.layer import render_layer
from plotmux.backends.matplotlib.line import render_line
from plotmux.backends.matplotlib.scatter import render_scatter
from plotmux.backends.matplotlib.style import apply_common_style
from plotmux.specs import BaseSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from matplotlib.figure import Figure as MplFigure

_SUPPORTED_FORMATS = frozenset({"png", "svg", "pdf", "jpg", "jpeg"})


def _render_histogram(spec: HistogramSpec, **kwargs: Any) -> MplFigure:
    fig, ax = plt.subplots()
    render_histogram(ax, spec, **kwargs)
    apply_common_style(ax, spec)
    return fig


def _render_line(spec: LineSpec, **kwargs: Any) -> MplFigure:
    fig, ax = plt.subplots()
    render_line(ax, spec, **kwargs)
    apply_common_style(ax, spec)
    return fig


def _render_scatter(spec: ScatterSpec, **kwargs: Any) -> MplFigure:
    fig, ax = plt.subplots()
    render_scatter(ax, spec, **kwargs)
    apply_common_style(ax, spec)
    return fig


def _render_layer(spec: LayerSpec, **kwargs: Any) -> MplFigure:
    fig, ax = plt.subplots()
    render_layer(ax, spec, **kwargs)
    apply_common_style(ax, spec)
    return fig


class MatplotlibBackend(Backend):
    r"""Implement the matplotlib rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "matplotlib"

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., MplFigure]]] = {
        HistogramSpec: _render_histogram,
        LineSpec: _render_line,
        ScatterSpec: _render_scatter,
        LayerSpec: _render_layer,
    }

    def render(self, spec: BaseSpec, **kwargs: Any) -> MplFigure:
        r"""Render a spec into a matplotlib ``Figure``.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional matplotlib-specific keyword
                arguments, forwarded to the underlying plotting
                call.

        Returns:
            The resulting matplotlib ``Figure``.

        Raises:
            NotImplementedError: if there is no matplotlib renderer
                registered for the type of ``spec``.
        """
        renderer = self._RENDERERS.get(type(spec))
        if renderer is None:
            msg = f"No matplotlib renderer registered for spec type {type(spec)}"
            raise NotImplementedError(msg)
        return renderer(spec, **kwargs)

    def save(self, native: MplFigure, path: Path, fmt: str) -> None:
        r"""Export a matplotlib ``Figure`` to a file.

        Args:
            native: The matplotlib ``Figure`` to export.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        if fmt not in _SUPPORTED_FORMATS:
            msg = (
                f"Unsupported export format {fmt!r} for the matplotlib backend. "
                f"Supported formats: {sorted(_SUPPORTED_FORMATS)}"
            )
            raise ValueError(msg)
        native.savefig(path, format=fmt)
