r"""Render a ``LayerSpec`` onto a shared matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any

from plotmux.backends.base import resolve_renderer
from plotmux.backends.matplotlib.bar import render_bar
from plotmux.backends.matplotlib.cdf import render_cdf
from plotmux.backends.matplotlib.histogram import render_histogram
from plotmux.backends.matplotlib.line import render_line
from plotmux.backends.matplotlib.scatter import render_scatter
from plotmux.backends.matplotlib.slope import render_slope
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    HistogramSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes

    from plotmux.specs import LayerSpec

# Reuses the per-type ``render_<type>(ax, spec)`` functions, one entry per type
# also registered in ``MatplotlibBackend._RENDERERS`` -- adding a new
# chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
_AX_RENDERERS: dict[type[BaseSpec], Callable[..., Axes]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    SlopeSpec: render_slope,
}


def render_layer(ax: Axes, spec: LayerSpec, **kwargs: Any) -> Axes:
    r"""Render a ``LayerSpec`` onto a shared matplotlib ``Axes``.

    Draws each child spec onto the same ``Axes``, in ``spec.layers``
    order, via that child's own ``render_<type>(ax, child_spec)``
    function -- the same functions used to render a standalone
    ``HistogramSpec``/``LineSpec``/``ScatterSpec``. Each child
    renderer also calls ``ax.legend()`` itself when its own ``label``
    is set, so the loop below does not strictly need to call it
    again. It does anyway, once, unconditionally after every child is
    drawn: relying on "the last labeled child's own call happens to
    reflect the full combined legend" is order-fragile -- it silently
    stops working the moment a future chart type's ``render_<type>``
    changes when or whether it calls ``ax.legend()`` itself. Calling
    ``ax.legend()`` once here, explicitly, after all children are
    drawn, is what actually guarantees the combined legend reflects
    every labeled child regardless of draw order or of what any
    individual child renderer does. ``Axes.legend()`` is a no-op
    (raises no error, adds no legend) when no artist is labeled, so
    this is safe even when no child has a ``label``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The layer spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            child's ``render_<type>`` call (e.g. a shared ``alpha``).

    Returns:
        The ``Axes`` the children were drawn onto.

    Raises:
        NotImplementedError: if ``spec.layers`` contains a spec type
            with no matplotlib renderer registered here.
    """
    for child in spec.layers:
        renderer = resolve_renderer(_AX_RENDERERS, child, "matplotlib")
        renderer(ax, child, **kwargs)
    if any(child.label is not None for child in spec.layers):
        ax.legend()
    return ax
