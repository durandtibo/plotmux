r"""Render a ``LineSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_line"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import DASH_STYLE, rgba_to_plotly

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import LineSpec


def render_line(
    fig: Figure, spec: LineSpec, *, row: int | None = None, col: int | None = None, **kwargs: Any
) -> Figure:
    r"""Render a ``LineSpec`` onto a plotly ``Figure``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The line spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Scatter``.

    Returns:
        The ``Figure`` the line was drawn onto.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``LineSpec.__post_init__``.
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
    line: dict[str, Any] = {"dash": DASH_STYLE.get(spec.linestyle, spec.linestyle)}
    if color is not None:
        line["color"] = color
    if spec.linewidth is not None:
        line["width"] = spec.linewidth
    kwargs.setdefault("line", line)
    fig.add_trace(go.Scatter(x=spec.x, y=spec.y, mode="lines", **kwargs), row=row, col=col)
    return fig
