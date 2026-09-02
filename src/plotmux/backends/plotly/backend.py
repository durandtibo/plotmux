r"""Contain the plotly ``Backend`` implementation.

This module is only imported when plotly is installed (see
``plotmux.backends.plotly.__init__``), so it can import plotly
unconditionally.
"""

from __future__ import annotations

__all__ = ["PlotlyBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

import plotly.graph_objects as go

from plotmux.backends.base import Backend, check_export_format
from plotmux.backends.plotly.bar import render_bar
from plotmux.backends.plotly.cdf import render_cdf
from plotmux.backends.plotly.grid import render_grid
from plotmux.backends.plotly.histogram import render_histogram
from plotmux.backends.plotly.layer import render_layer
from plotmux.backends.plotly.line import render_line
from plotmux.backends.plotly.scatter import render_scatter
from plotmux.backends.plotly.style import apply_common_style
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

    from plotly.graph_objects import Figure


def _make_renderer(
    fig_render: Callable[..., Figure],
) -> Callable[..., Figure]:
    r"""Build a ``render(spec, **kwargs) -> Figure`` function from a
    ``fig_render(fig, spec, **kwargs) -> Figure`` function.

    Every entry in ``_RENDERERS`` shares the same three steps: create
    a ``go.Figure``, draw the spec-specific trace(s) onto it via
    ``fig_render``, then apply the fields common to every chart type
    (title, labels, scale, ...) via ``apply_common_style``. Factoring
    that out here means adding a new chart type to this backend is
    exactly one ``_RENDERERS`` entry -- ``_make_renderer(render_x)``
    -- rather than a new hand-written wrapper function that repeats
    the same three lines. Mirrors
    ``plotmux.backends.bokeh.backend._make_renderer``. Unlike bokeh's
    axis type (a construction-time argument of ``bokeh.plotting.figure``),
    plotly's ``xaxis_type``/``yaxis_type`` can be set after the trace
    is drawn, via ``apply_common_style``'s own ``fig.update_layout``
    call, so no axis-type wiring is needed here at construction time.

    Args:
        fig_render: The chart-specific ``(fig, spec, **kwargs) ->
            Figure`` renderer to wrap, e.g. ``render_histogram``.

    Returns:
        A ``(spec, **kwargs) -> Figure`` renderer suitable for
            ``_RENDERERS``.
    """

    def render(spec: BaseSpec, **kwargs: Any) -> Figure:
        fig = go.Figure()
        fig_render(fig, spec, **kwargs)
        apply_common_style(fig, spec)
        return fig

    return render


class PlotlyBackend(Backend):
    r"""Implement the plotly rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.

    ``SlopeSpec`` is deliberately absent: unlike matplotlib/bokeh,
    plotly has no native "line by slope, independent of data range"
    primitive, so (same as altair/xy) it is only supported as a
    ``LayerSpec`` child -- see ``plotmux.backends.plotly.slope`` and
    DESIGN.md, section 8.1.
    """

    name: ClassVar[str] = "plotly"
    # ``html``: plotly's own native, dependency-free export path
    # (``Figure.write_html``), the format that best matches why a plotly
    # backend is worth having -- interactive, standalone HTML output, same
    # rationale as bokeh's ``html``-only ``supported_formats`` (see
    # ``plotmux.backends.bokeh.backend.BokehBackend``). Static image export
    # (``png``/``svg``/``pdf``) goes through ``Figure.write_image``, which
    # additionally requires the ``kaleido`` package -- a heavier,
    # environment-specific dependency than "pip install plotly", mirroring
    # bokeh's Selenium-webdriver gap and altair's ``vl-convert-python`` gap.
    # ``json``: plotly's other dependency-free export path
    # (``Figure.write_json``), same rationale as altair's ``json`` format.
    supported_formats: ClassVar[frozenset[str]] = frozenset({"html", "json"})

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., Figure]]] = {
        HistogramSpec: _make_renderer(render_histogram),
        BarSpec: _make_renderer(render_bar),
        CdfSpec: _make_renderer(render_cdf),
        LineSpec: _make_renderer(render_line),
        ScatterSpec: _make_renderer(render_scatter),
        LayerSpec: _make_renderer(render_layer),
        # ``render_grid`` builds its own ``Figure`` via
        # ``plotly.subplots.make_subplots`` rather than drawing onto one
        # figure built here -- it does not fit ``_make_renderer``'s "one
        # figure, one fig_render call" shape, so it is registered directly
        # instead of wrapped.
        GridSpec: render_grid,
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

    def save(self, native: Figure, path: Path, fmt: str) -> None:
        r"""Export a plotly ``Figure`` to a file.

        Args:
            native: The plotly ``Figure`` to export.
            path: The path where to save the figure.
            fmt: The export format. ``"html"`` or ``"json"`` (see
                ``supported_formats``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        check_export_format(fmt, self.supported_formats, self.name)
        if fmt == "html":
            native.write_html(str(path))
        else:
            native.write_json(str(path))
