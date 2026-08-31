r"""Render a ``GridSpec`` into a grid of independent bokeh
``figure``s."""

from __future__ import annotations

__all__ = ["render_grid"]

from html import escape
from typing import TYPE_CHECKING, Any

from bokeh.layouts import column, gridplot
from bokeh.models import Div
from bokeh.plotting import figure as bokeh_figure

from plotmux.backends.base import resolve_renderer
from plotmux.backends.bokeh.cdf import render_cdf
from plotmux.backends.bokeh.histogram import render_histogram
from plotmux.backends.bokeh.layer import render_layer
from plotmux.backends.bokeh.line import render_line
from plotmux.backends.bokeh.scatter import render_scatter
from plotmux.backends.bokeh.style import apply_common_style
from plotmux.specs import BaseSpec, CdfSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable

    from bokeh.models import LayoutDOM
    from bokeh.plotting import figure

    from plotmux.specs import GridSpec

# Reuses the per-type ``render_<type>(fig, spec)`` functions, one entry per type
# also registered in ``BokehBackend._RENDERERS`` -- adding a new chart type
# there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``). Includes
# ``LayerSpec`` (unlike ``plotmux.backends.bokeh.layer``'s own
# ``_FIG_RENDERERS``): a grid cell may itself be several series sharing one
# panel's figure, since layering and gridding are independent, composable
# concerns -- only a ``GridSpec`` nested inside another ``GridSpec`` is
# rejected (see ``GridSpec.__post_init__``).
_FIG_RENDERERS: dict[type[BaseSpec], Callable[..., figure]] = {
    HistogramSpec: render_histogram,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    LayerSpec: render_layer,
}


def render_grid(spec: GridSpec, **kwargs: Any) -> LayoutDOM:
    r"""Render a ``GridSpec`` into a grid of independent bokeh
    ``figure``s.

    Builds one independent bokeh ``figure`` per cell -- the same way
    ``BokehBackend``'s own ``_make_renderer`` builds one for a
    standalone chart -- draws and styles it via that cell's own
    ``render_<type>(fig, cell)``/``apply_common_style``, then arranges
    every cell's ``figure`` with ``bokeh.layouts.gridplot`` (bokeh has
    no single-``figure`` notion of subplots the way matplotlib's
    ``Axes`` array does, so composition happens at the layout level
    instead).

    ``spec.title``, when set, cannot be attached to any single cell
    ``figure`` (it describes the whole grid, not one panel), so it is
    rendered as a heading ``Div`` placed above the ``gridplot`` in a
    ``column`` -- the closest bokeh equivalent of matplotlib's
    ``Figure.suptitle`` (see
    ``plotmux.backends.matplotlib.grid.render_grid``).

    Args:
        spec: The grid spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            cell's ``render_<type>`` call.

    Returns:
        The resulting bokeh layout: a ``gridplot`` alone, or a
            ``column`` of a title ``Div`` above the ``gridplot`` when
            ``spec.title`` is set.

    Raises:
        NotImplementedError: if ``spec.cells`` contains a spec type
            with no bokeh renderer registered here.
    """
    figs = []
    for cell in spec.cells:
        fig = bokeh_figure(x_axis_type=cell.xscale, y_axis_type=cell.yscale)
        renderer = resolve_renderer(_FIG_RENDERERS, cell, "bokeh")
        renderer(fig, cell, **kwargs)
        apply_common_style(fig, cell)
        figs.append(fig)
    rows = [figs[i : i + spec.ncols] for i in range(0, len(figs), spec.ncols)]
    grid = gridplot(rows)
    if spec.title is not None:
        return column(Div(text=f"<h2>{escape(spec.title)}</h2>"), grid)
    return grid
