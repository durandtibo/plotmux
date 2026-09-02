r"""Render a ``SlopeSpec`` into a plotly ``Figure``, given the x-range
it should span."""

from __future__ import annotations

__all__ = ["render_slope"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import DASH_STYLE, rgba_to_plotly

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import SlopeSpec


def render_slope(
    fig: Figure,
    spec: SlopeSpec,
    xrange: tuple[float, float],
    *,
    row: int | None = None,
    col: int | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Render a ``SlopeSpec`` into a plotly ``Figure``.

    Unlike matplotlib's ``Axes.axline``/bokeh's ``bokeh.models.Slope``
    (see ``plotmux.backends.matplotlib.slope``/
    ``plotmux.backends.bokeh.slope``), plotly has no native "line by
    slope, independent of data range" primitive either: its own
    ``add_shape``/``add_hline``/``add_vline`` annotations either need
    concrete data-space endpoints or only cover the horizontal/
    vertical special cases, and drawing between two arbitrary
    far-apart points would blow out plotly's own default autorange
    (the same problem noted for altair/xy in DESIGN.md, section 8.1).
    So, like ``plotmux.backends.altair.slope.render_slope``/
    ``plotmux.backends.xy.slope.render_slope``, this draws a plain
    two-point ``go.Scatter`` line between ``(xrange[0], gradient *
    xrange[0] + intercept)`` and ``(xrange[1], gradient * xrange[1] +
    intercept)`` -- ``xrange`` is supplied by the caller
    (``plotmux.backends.plotly.layer.render_layer``, via
    ``plotmux.utils.slope.resolve_slope_xrange``), computed from the
    ``SlopeSpec``'s sibling children in the same ``LayerSpec``, since
    a standalone ``SlopeSpec`` has no data of its own to derive a
    range from. This renderer is registered only in ``render_layer``'s
    own dispatch table, not in ``PlotlyBackend._RENDERERS``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The slope spec to render.
        xrange: The ``(min, max)`` x-range the line should span,
            computed from ``spec``'s siblings.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Scatter``.

    Returns:
        The ``Figure`` the line was drawn onto.
    """
    x0, x1 = xrange
    y0 = spec.gradient * x0 + spec.intercept
    y1 = spec.gradient * x1 + spec.intercept
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``SlopeSpec.__post_init__``.
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
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", **kwargs), row=row, col=col)
    return fig
