r"""Render a ``GridSpec`` into a grid of independent plotly subplots."""

from __future__ import annotations

__all__ = ["render_grid"]

import math
from html import escape
from typing import TYPE_CHECKING, Any

from plotly.subplots import make_subplots

from plotmux.backends.base import resolve_renderer
from plotmux.backends.plotly.bar import render_bar
from plotmux.backends.plotly.cdf import render_cdf
from plotmux.backends.plotly.histogram import render_histogram
from plotmux.backends.plotly.layer import render_layer
from plotmux.backends.plotly.line import render_line
from plotmux.backends.plotly.scatter import render_scatter
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotly.graph_objects import Figure

    from plotmux.specs import GridSpec

# Reuses the per-type ``render_<type>(fig, spec, row=, col=)`` functions,
# one entry per type also registered in ``PlotlyBackend._RENDERERS`` --
# adding a new chart type there means adding one entry here too, following
# the same ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
# Includes ``LayerSpec`` (unlike ``plotmux.backends.plotly.layer``'s own
# ``_TRACE_RENDERERS``): a grid cell may itself be several series sharing
# one panel's axes, since layering and gridding are independent, composable
# concerns -- only a ``GridSpec`` nested inside another ``GridSpec`` is
# rejected (see ``GridSpec.__post_init__``). Mirrors
# ``plotmux.backends.bokeh.grid``.
_CELL_RENDERERS: dict[type[BaseSpec], Callable[..., Figure]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    LayerSpec: render_layer,
}


def render_grid(spec: GridSpec, **kwargs: Any) -> Figure:
    r"""Render a ``GridSpec`` into a grid of independent plotly subplots.

    Unlike bokeh/altair (composing several independent, already-built
    figures via ``gridplot``/``alt.concat``, see
    ``plotmux.backends.bokeh.grid``/``plotmux.backends.altair.grid``),
    plotly has a native subplot-grid primitive,
    ``plotly.subplots.make_subplots``, matching matplotlib's own
    ``pyplot.subplots`` fairly closely: it returns one ``Figure``
    whose distinct ``xaxis``/``yaxis`` pairs each cell's own
    ``render_<type>(fig, cell, row=, col=)`` call draws onto (via
    ``go.Figure.add_trace(..., row=, col=)``), rather than building
    ``len(cells)`` independent ``Figure``s and composing them
    afterwards.

    plotly's ``title`` is figure-level (there is only one), so it
    cannot host each cell's own ``spec.title`` the way a standalone
    chart's ``apply_common_style`` does; instead, every cell's title
    (or ``""`` for an unset one) is passed to
    ``make_subplots(subplot_titles=...)``, plotly's own per-subplot
    heading annotation. ``spec.title`` (the whole grid's own title),
    when set, is applied afterwards via ``fig.update_layout(title=...)``
    -- the closest plotly equivalent of matplotlib's
    ``Figure.suptitle``/bokeh's heading ``Div`` (see
    ``plotmux.backends.bokeh.grid.render_grid``).

    Args:
        spec: The grid spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            cell's ``render_<type>`` call.

    Returns:
        The resulting plotly ``Figure``, laid out as a
            ``spec.ncols``-wide grid of subplots.

    Raises:
        NotImplementedError: if ``spec.cells`` contains a spec type
            with no plotly renderer registered here.
    """
    nrows = math.ceil(len(spec.cells) / spec.ncols)
    # ``escape``: a cell title is rendered as an annotation, which plotly
    # (like bokeh's heading ``Div``, see ``plotmux.backends.bokeh.grid``)
    # treats as markup capable of embedding tags, not plain text.
    subplot_titles = [escape(cell.title) if cell.title is not None else "" for cell in spec.cells]
    fig = make_subplots(rows=nrows, cols=spec.ncols, subplot_titles=subplot_titles)
    for i, cell in enumerate(spec.cells):
        row, col = i // spec.ncols + 1, i % spec.ncols + 1
        renderer = resolve_renderer(_CELL_RENDERERS, cell, "plotly")
        renderer(fig, cell, row=row, col=col, **kwargs)
        if cell.xlabel is not None:
            fig.update_xaxes(title_text=cell.xlabel, row=row, col=col)
        if cell.ylabel is not None:
            fig.update_yaxes(title_text=cell.ylabel, row=row, col=col)
        fig.update_xaxes(type=cell.xscale, row=row, col=col)
        fig.update_yaxes(type=cell.yscale, row=row, col=col)
        # Same "both bounds together, or neither" rule as
        # ``plotmux.backends.plotly.style.apply_common_style``.
        if cell.ymin is not None and cell.ymax is not None:
            fig.update_yaxes(range=[cell.ymin, cell.ymax], row=row, col=col)
    if spec.title is not None:
        fig.update_layout(title=spec.title)
    return fig
