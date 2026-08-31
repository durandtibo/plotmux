r"""Render a ``GridSpec`` into a matplotlib ``Figure`` of independent
subplots."""

from __future__ import annotations

__all__ = ["render_grid"]

import math
from typing import TYPE_CHECKING, Any

from matplotlib.figure import Figure as MplFigure

from plotmux.backends.base import resolve_renderer
from plotmux.backends.matplotlib.cdf import render_cdf
from plotmux.backends.matplotlib.histogram import render_histogram
from plotmux.backends.matplotlib.layer import render_layer
from plotmux.backends.matplotlib.line import render_line
from plotmux.backends.matplotlib.scatter import render_scatter
from plotmux.backends.matplotlib.style import apply_common_style, attach_repr_png
from plotmux.specs import (
    BaseSpec,
    CdfSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes

    from plotmux.specs import GridSpec

# Reuses the per-type ``render_<type>(ax, spec)`` functions, one entry per type
# also registered in ``MatplotlibBackend._RENDERERS`` -- adding a new
# chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``). Includes
# ``LayerSpec`` (unlike ``plotmux.backends.matplotlib.layer``'s own
# ``_AX_RENDERERS``): a grid cell may itself be several series sharing one
# panel's axes, since layering and gridding are independent, composable
# concerns -- only a ``GridSpec`` nested inside another ``GridSpec`` is
# rejected (see ``GridSpec.__post_init__``).
_AX_RENDERERS: dict[type[BaseSpec], Callable[..., Axes]] = {
    HistogramSpec: render_histogram,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    LayerSpec: render_layer,
}


def render_grid(spec: GridSpec, **kwargs: Any) -> MplFigure:
    r"""Render a ``GridSpec`` into a matplotlib ``Figure`` of
    independent subplots.

    Builds one ``Figure`` with ``nrows x spec.ncols`` subplots
    (``nrows = ceil(len(spec.cells) / spec.ncols)``), draws each cell
    onto its own ``Axes`` via that cell's own ``render_<type>(ax,
    cell)`` function, then styles that ``Axes`` with the cell's own
    ``apply_common_style`` -- each panel keeps its own title/labels/
    scale, unlike ``LayerSpec`` where those are shared across every
    child (see ``plotmux.backends.matplotlib.layer.render_layer``).
    Any trailing subplot left over when ``len(spec.cells)`` is not a
    multiple of ``spec.ncols`` is hidden rather than left blank but
    visible.

    Args:
        spec: The grid spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            cell's ``render_<type>`` call.

    Returns:
        The resulting matplotlib ``Figure``.

    Raises:
        NotImplementedError: if ``spec.cells`` contains a spec type
            with no matplotlib renderer registered here.
    """
    nrows = math.ceil(len(spec.cells) / spec.ncols)
    fig = MplFigure()
    axes = fig.subplots(nrows, spec.ncols, squeeze=False)
    flat_axes = [ax for row in axes for ax in row]
    for ax, cell in zip(flat_axes, spec.cells, strict=False):
        renderer = resolve_renderer(_AX_RENDERERS, cell, "matplotlib")
        renderer(ax, cell, **kwargs)
        apply_common_style(ax, cell)
    for ax in flat_axes[len(spec.cells) :]:
        ax.set_visible(False)
    if spec.title is not None:
        fig.suptitle(spec.title)
    attach_repr_png(fig)
    return fig
