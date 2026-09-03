r"""Render a ``ScatterSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import MARKER_STYLE, rgba_to_plotly

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import ScatterSpec


def render_scatter(
    fig: Figure,
    spec: ScatterSpec,
    *,
    row: int | None = None,
    col: int | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Render a ``ScatterSpec`` onto a plotly ``Figure``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The scatter spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Scatter``.

    Returns:
        The ``Figure`` the markers were drawn onto.
    """
    # ``spec.color``/``spec.edgecolor``, once set, are already canonical
    # RGBA tuples: they went through ``parse_color`` in
    # ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_plotly(cast("tuple[float, float, float, float]", spec.color))
    )
    edgecolor = (
        color
        if spec.edgecolor is None
        else rgba_to_plotly(cast("tuple[float, float, float, float]", spec.edgecolor))
    )
    if spec.label is not None:
        kwargs.setdefault("name", spec.label)
        kwargs.setdefault("showlegend", True)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    marker: dict[str, Any] = {}
    if color is not None:
        marker["color"] = color
    if spec.size is not None:
        marker["size"] = spec.size
    # A non-zero border width is required for ``edgecolor`` to actually be
    # visible (plotly's own marker border defaults to width 0); always set
    # when either color is known, mirroring
    # ``plotmux.backends.bokeh.scatter.render_scatter`` always passing
    # ``line_color`` (defaulting to ``color``) rather than only when
    # ``spec.edgecolor`` is explicitly set.
    if edgecolor is not None:
        marker["line"] = {"color": edgecolor, "width": 1}
    if spec.fill is False:
        # plotly has no "no fill" marker property, only an explicit color
        # (unlike bokeh's ``fill_color=None``/altair's
        # ``mark_point(filled=False)``, see
        # ``plotmux.backends.bokeh.scatter.render_scatter``/
        # ``plotmux.backends.altair.scatter.render_scatter``), so the fill
        # is forced fully transparent instead; the outline (already set
        # above from ``edgecolor``, else ``color``) stays visible.
        marker["color"] = "rgba(0, 0, 0, 0)"
        marker.setdefault("line", {"color": color, "width": 1})
    if spec.marker is not None:
        marker["symbol"] = MARKER_STYLE[spec.marker]
    kwargs.setdefault("marker", marker)
    fig.add_trace(go.Scatter(x=spec.x, y=spec.y, mode="markers", **kwargs), row=row, col=col)
    return fig
