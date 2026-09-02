r"""Render a ``BarSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_bar"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import rgba_to_plotly

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import BarSpec


def render_bar(
    fig: Figure, spec: BarSpec, *, row: int | None = None, col: int | None = None, **kwargs: Any
) -> Figure:
    r"""Render a ``BarSpec`` onto a plotly ``Figure``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The bar spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Bar``.

    Returns:
        The ``Figure`` the bars were drawn onto.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``BarSpec.__post_init__``.
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
        go.Bar(x=spec.x, y=spec.y, width=spec.width, marker_color=color, **kwargs),
        row=row,
        col=col,
    )
    return fig
