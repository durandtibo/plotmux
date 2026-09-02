r"""Render a ``HistogramSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any, cast

import numpy as np
import plotly.graph_objects as go

from plotmux.backends.plotly.style import rgba_to_plotly
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import HistogramSpec


def render_histogram(
    fig: Figure,
    spec: HistogramSpec,
    *,
    row: int | None = None,
    col: int | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Render a ``HistogramSpec`` onto a plotly ``Figure``.

    plotly's own ``go.Histogram`` bins its input trace-side, with no
    way to hand it precomputed ``xmin``/``xmax`` bounds the way
    ``spec.xmin``/``spec.xmax`` require, so (same approach as
    ``plotmux.backends.bokeh.histogram.render_histogram``) the bin
    counts and edges are computed with ``numpy.histogram`` and drawn
    as a ``go.Bar``, one rectangle per bin.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The histogram spec to render.
        row: The 1-indexed subplot row to draw onto, when ``fig`` was
            built with ``plotly.subplots.make_subplots`` (see
            ``plotmux.backends.plotly.grid.render_grid``). ``None``
            draws onto ``fig``'s only axes.
        col: The 1-indexed subplot column to draw onto. Same
            semantics as ``row``.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Bar``.

    Returns:
        The ``Figure`` the histogram was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    counts, edges = np.histogram(
        spec.values, bins=spec.bins, range=(xmin, xmax), density=spec.density
    )
    centers = (edges[:-1] + edges[1:]) / 2
    width = edges[1] - edges[0]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``HistogramSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_plotly(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.label is not None:
        kwargs.setdefault("name", spec.label)
        kwargs.setdefault("showlegend", True)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    fig.add_trace(
        go.Bar(x=centers, y=counts, width=width, marker_color=color, **kwargs), row=row, col=col
    )
    return fig
