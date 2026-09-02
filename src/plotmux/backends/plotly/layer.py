r"""Render a ``LayerSpec`` onto a shared plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any

from plotmux.backends.base import resolve_renderer
from plotmux.backends.plotly.bar import render_bar
from plotmux.backends.plotly.cdf import render_cdf
from plotmux.backends.plotly.histogram import render_histogram
from plotmux.backends.plotly.line import render_line
from plotmux.backends.plotly.scatter import render_scatter
from plotmux.backends.plotly.slope import render_slope
from plotmux.exceptions import UnsupportedSpecError
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    HistogramSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)
from plotmux.utils.slope import resolve_slope_xrange

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotly.graph_objects import Figure

    from plotmux.specs import LayerSpec

# Reuses the per-type ``render_<type>(fig, spec)`` functions, one entry
# per type also registered in ``PlotlyBackend._RENDERERS`` -- adding a new
# chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
#
# ``SlopeSpec`` is *not* registered in ``PlotlyBackend._RENDERERS`` (unlike
# every other entry here): it is only supported as a ``LayerSpec`` child,
# since ``render_slope`` needs an ``xrange`` computed from its siblings (see
# ``plotmux.utils.slope.resolve_slope_xrange``), which a standalone spec has
# no way to supply (see DESIGN.md, section 8.1, and
# ``plotmux.backends.plotly.slope`` for why plotly follows altair/xy here
# rather than matplotlib/bokeh). It is still listed here so
# ``resolve_renderer`` recognizes the type below; the actual call passes
# ``xrange`` explicitly rather than going through the generic
# ``renderer(fig, child, **kwargs)`` call every other type uses.
_TRACE_RENDERERS: dict[type[BaseSpec], Callable[..., Figure]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    SlopeSpec: render_slope,
}


def render_layer(
    fig: Figure, spec: LayerSpec, *, row: int | None = None, col: int | None = None, **kwargs: Any
) -> Figure:
    r"""Render a ``LayerSpec`` onto a shared plotly ``Figure``.

    Draws each child spec onto the same ``Figure`` (or, inside a
    ``GridSpec`` cell, the same subplot axes -- see ``row``/``col``),
    in ``spec.layers`` order, via that child's own
    ``render_<type>(fig, child_spec)`` function -- the same functions
    used to render a standalone ``HistogramSpec``/``LineSpec``/
    ``ScatterSpec``. Same shared-figure approach as
    ``plotmux.backends.bokeh.layer.render_layer``. Each labeled
    child's own ``name``/``showlegend=True`` (set by its own
    ``render_<type>``) is enough for plotly to add it to the combined
    legend automatically, so no explicit "combine the legend" step is
    needed here, unlike matplotlib's ``Axes.legend()``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The layer spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to every
            child's ``render_<type>`` call.

    Returns:
        The ``Figure`` the children were drawn onto.

    Raises:
        NotImplementedError: if ``spec.layers`` contains a spec type
            with no plotly renderer registered here.
        ValueError: if ``spec.layers`` contains a ``SlopeSpec`` with
            no data-bound sibling to derive an x-range from. Also a
            ``NotImplementedError`` (``UnsupportedSpecError``).
    """
    # Computed once, up front, from every child (not lazily inside the loop
    # below): a ``SlopeSpec`` may come before its data-bound sibling in
    # draw order, and the range does not depend on which ``SlopeSpec`` is
    # asking, so one shared computation covers every ``SlopeSpec`` child.
    # Mirrors ``plotmux.backends.altair.layer.render_layer``.
    xrange = None
    if any(isinstance(child, SlopeSpec) for child in spec.layers):
        xrange = resolve_slope_xrange(spec.layers)
        if xrange is None:
            msg = (
                "plotly cannot render a SlopeSpec with no data-bound sibling "
                "in the same layer() call to derive an x-range from -- "
                "plotly has no native line-by-slope primitive (see "
                "DESIGN.md, section 8.1), unlike matplotlib/bokeh."
            )
            raise UnsupportedSpecError(msg)
    for child in spec.layers:
        renderer = resolve_renderer(_TRACE_RENDERERS, child, "plotly")
        if isinstance(child, SlopeSpec):
            renderer(fig, child, xrange=xrange, row=row, col=col, **kwargs)
        else:
            renderer(fig, child, row=row, col=col, **kwargs)
    return fig
