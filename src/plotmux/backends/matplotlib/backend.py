r"""Contain the matplotlib ``Backend`` implementation.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["MatplotlibBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

from matplotlib.figure import Figure as MplFigure

from plotmux.backends.base import Backend, check_export_format
from plotmux.backends.matplotlib.bar import render_bar
from plotmux.backends.matplotlib.cdf import render_cdf
from plotmux.backends.matplotlib.grid import render_grid
from plotmux.backends.matplotlib.histogram import render_histogram
from plotmux.backends.matplotlib.layer import render_layer
from plotmux.backends.matplotlib.line import render_line
from plotmux.backends.matplotlib.scatter import render_scatter
from plotmux.backends.matplotlib.style import apply_common_style, attach_repr_png
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from matplotlib.axes import Axes


def _make_renderer(
    ax_render: Callable[..., Axes],
) -> Callable[..., MplFigure]:
    r"""Build a ``render(spec, **kwargs) -> MplFigure`` function from an
    ``ax_render(ax, spec, **kwargs) -> Axes`` function.

    Every entry in ``_RENDERERS`` shares the same three steps: create
    a figure/axes pair, draw the spec-specific mark onto it via
    ``ax_render``, then apply the fields common to every chart type
    (title, labels, scales) via ``apply_common_style``. Factoring
    that out here means adding a new chart type to this backend is
    exactly one ``_RENDERERS`` entry -- ``_make_renderer(render_x)``
    -- rather than a new hand-written wrapper function that repeats
    the same three lines.

    The figure is built via the ``matplotlib.figure.Figure``
    constructor rather than ``pyplot.subplots()``: the latter
    registers the figure with pyplot's global figure manager, so
    figures created that way are never garbage-collected until
    ``plt.close()`` is called on them explicitly -- a real memory
    leak for any code that renders many figures (e.g. one histogram
    per column, in a loop or notebook). Building the ``Figure``
    directly keeps it a plain, independently garbage-collectable
    object with no such global registration.

    Args:
        ax_render: The chart-specific ``(ax, spec, **kwargs) -> Axes``
            renderer to wrap, e.g. ``render_histogram``.

    Returns:
        A ``(spec, **kwargs) -> MplFigure`` renderer suitable for
            ``_RENDERERS``.
    """

    def render(spec: BaseSpec, **kwargs: Any) -> MplFigure:
        fig = MplFigure()
        ax = fig.subplots()
        ax_render(ax, spec, **kwargs)
        apply_common_style(ax, spec)
        attach_repr_png(fig)
        return fig

    return render


class MatplotlibBackend(Backend):
    r"""Implement the matplotlib rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "matplotlib"
    supported_formats: ClassVar[frozenset[str]] = frozenset({"png", "svg", "pdf", "jpg", "jpeg"})

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., MplFigure]]] = {
        HistogramSpec: _make_renderer(render_histogram),
        BarSpec: _make_renderer(render_bar),
        CdfSpec: _make_renderer(render_cdf),
        LineSpec: _make_renderer(render_line),
        ScatterSpec: _make_renderer(render_scatter),
        LayerSpec: _make_renderer(render_layer),
        # ``render_grid`` builds and styles its own ``Figure`` (one subplot
        # per cell, each individually styled) rather than a single shared
        # ``Axes`` -- it does not fit ``_make_renderer``'s
        # "one figure, one ax_render call" shape, so it is registered
        # directly instead of wrapped.
        GridSpec: render_grid,
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

    def save(self, native: MplFigure, path: Path, fmt: str) -> None:
        r"""Export a matplotlib ``Figure`` to a file.

        Args:
            native: The matplotlib ``Figure`` to export.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        check_export_format(fmt, self.supported_formats, self.name)
        native.savefig(path, format=fmt)
