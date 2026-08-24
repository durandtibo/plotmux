r"""Render a ``LayerSpec`` onto a shared matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any

from plotmux.backends.matplotlib.histogram import render_histogram
from plotmux.backends.matplotlib.line import render_line
from plotmux.backends.matplotlib.scatter import render_scatter
from plotmux.specs import BaseSpec, HistogramSpec, LineSpec, ScatterSpec

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
    LineSpec: render_line,
    ScatterSpec: render_scatter,
}


def render_layer(ax: Axes, spec: LayerSpec, **kwargs: Any) -> Axes:
    r"""Render a ``LayerSpec`` onto a shared matplotlib ``Axes``.

    Draws each child spec onto the same ``Axes``, in ``spec.layers``
    order, via that child's own ``render_<type>(ax, child_spec)``
    function -- the same functions used to render a standalone
    ``HistogramSpec``/``LineSpec``/``ScatterSpec``. No separate
    ``ax.legend()`` call is needed here: each child renderer already
    calls ``ax.legend()`` when its own ``label`` is set, and
    matplotlib's ``Axes.legend()`` collects every currently-plotted
    labeled artist at call time, so the last labeled child's call
    ends up reflecting the full combined legend.

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
        renderer = _AX_RENDERERS.get(type(child))
        if renderer is None:
            msg = f"No matplotlib renderer registered for spec type {type(child)}"
            raise NotImplementedError(msg)
        renderer(ax, child, **kwargs)
    return ax
