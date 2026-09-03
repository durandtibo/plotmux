r"""Render a ``StackedBarSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_stacked_bar"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import rgba_to_plotly

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import StackedBarSpec


def render_stacked_bar(
    fig: Figure,
    spec: StackedBarSpec,
    *,
    row: int | None = None,
    col: int | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Render a ``StackedBarSpec`` onto a plotly ``Figure``.

    Adds one ``go.Bar`` trace per series, plus
    ``fig.update_layout(barmode="stack")`` -- plotly has no
    per-trace stacking argument, only a figure-wide layout mode, so
    every ``go.Bar`` trace already on ``fig`` (e.g. from an earlier
    ``StackedBarSpec``, or a plain ``BarSpec`` layered alongside)
    would also stack; a fresh ``Figure`` (as every ``_RENDERERS``
    entry constructs, see
    ``plotmux.backends.plotly.backend._make_renderer``) keeps this
    scoped to just this spec's own traces.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The stacked-bar spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to every
            ``go.Bar`` trace.

    Returns:
        The ``Figure`` the bars were drawn onto.
    """
    for series in spec.series:
        # Every series' ``color``, once set, is already a canonical RGBA
        # tuple: it went through ``parse_color`` in
        # ``StackedBarSpec.__post_init__``.
        color = rgba_to_plotly(cast("tuple[float, float, float, float]", series.color))
        trace_kwargs: dict[str, Any] = {**kwargs}
        if series.label is not None:
            trace_kwargs.setdefault("name", series.label)
            trace_kwargs.setdefault("showlegend", True)
        if spec.alpha is not None:
            trace_kwargs.setdefault("opacity", spec.alpha)
        fig.add_trace(
            go.Bar(x=spec.x, y=series.y, width=spec.width, marker_color=color, **trace_kwargs),
            row=row,
            col=col,
        )
    fig.update_layout(barmode="stack")
    return fig
