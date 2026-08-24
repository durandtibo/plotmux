r"""Render a ``LayerSpec`` onto a shared bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any

from plotmux.backends.base import resolve_renderer
from plotmux.backends.bokeh.histogram import render_histogram
from plotmux.backends.bokeh.line import render_line
from plotmux.backends.bokeh.scatter import render_scatter
from plotmux.specs import BaseSpec, HistogramSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable

    from bokeh.plotting import figure

    from plotmux.specs import LayerSpec

# Reuses the per-type ``render_<type>(fig, spec)`` functions, one entry per type
# also registered in ``BokehBackend._RENDERERS`` -- adding a new chart type
# there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
_FIG_RENDERERS: dict[type[BaseSpec], Callable[..., figure]] = {
    HistogramSpec: render_histogram,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
}


def render_layer(fig: figure, spec: LayerSpec, **kwargs: Any) -> figure:
    r"""Render a ``LayerSpec`` onto a shared bokeh ``figure``.

    Draws each child spec onto the same ``figure``, in ``spec.layers``
    order, via that child's own ``render_<type>(fig, child_spec)``
    function -- the same functions used to render a standalone
    ``HistogramSpec``/``LineSpec``/``ScatterSpec``. Each labeled child
    glyph is automatically added to ``fig.legend`` by bokeh itself
    (through its own ``legend_label`` kwarg), so no explicit
    "combine the legend" step is needed here, unlike matplotlib's
    ``Axes.legend()`` (see ``plotmux.backends.matplotlib.layer``).

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The layer spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            child's ``render_<type>`` call (e.g. a shared
            ``line_width``).

    Returns:
        The ``figure`` the children were drawn onto.

    Raises:
        NotImplementedError: if ``spec.layers`` contains a spec type
            with no bokeh renderer registered here.
    """
    for child in spec.layers:
        renderer = resolve_renderer(_FIG_RENDERERS, child, "bokeh")
        renderer(fig, child, **kwargs)
    return fig
