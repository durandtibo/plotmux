r"""Apply the common figure-level style fields onto a plotly ``Figure``.

This module is only imported when plotly is installed (see
``plotmux.backends.plotly.__init__``), so it can import plotly
unconditionally.
"""

from __future__ import annotations

__all__ = ["DASH_STYLE", "MARKER_STYLE", "apply_common_style", "rgba_to_plotly"]

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import BaseSpec

#: Maps plotmux's dash-style names (shared by ``LineSpec``/``SlopeSpec``)
#: to plotly's own ``line.dash`` values. Only ``"dotted"`` differs
#: from plotmux's name (plotly calls it ``"dot"``); the rest match
#: plotmux's own vocabulary already, unlike e.g. altair's pixel-list
#: ``strokeDash`` (see ``plotmux.backends.altair.style.STROKE_DASH``).
DASH_STYLE: dict[str, str] = {
    "solid": "solid",
    "dashed": "dash",
    "dotted": "dot",
    "dashdot": "dashdot",
}

#: Maps ``ScatterSpec.marker``'s portable shape name to plotly's
#: ``go.Scatter(marker_symbol=...)`` value. Every one of plotmux's six
#: portable names has a direct plotly equivalent, unlike altair (see
#: ``plotmux.backends.altair.style.MARKER_STYLE``).
MARKER_STYLE: dict[str, str] = {
    "circle": "circle",
    "square": "square",
    "triangle": "triangle-up",
    "diamond": "diamond",
    "cross": "cross",
    "x": "x",
}


def rgba_to_plotly(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to plotly's native color type.

    plotly's trace/marker color parameters accept a CSS-style
    ``"rgba(r, g, b, a)"`` string, so the canonical ``[0, 1]`` float
    RGBA tuple produced by ``plotmux.colors.parse_color`` is converted
    to that format here rather than in ``core/``, keeping ``core/``
    free of any single backend's native color representation -- same
    pattern as ``plotmux.backends.bokeh.style.rgba_to_bokeh``/
    ``plotmux.backends.xy.style.rgba_to_xy``.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as an ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a`` as
            a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.plotly.style import rgba_to_plotly
        >>> rgba_to_plotly((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"


def apply_common_style(fig: Figure, spec: BaseSpec) -> Figure:
    r"""Apply the common figure-level style fields onto a plotly
    ``Figure``.

    Applies ``title``/``xlabel``/``ylabel``/``xscale``/``yscale``/
    ``background_color``/``ymin``/``ymax``/``legend_title`` from
    ``spec`` (defined on ``BaseSpec``, shared by every chart type).
    Called once per
    standalone figure or ``LayerSpec``, right after every trace has
    been added, via ``fig.update_layout`` -- unlike bokeh's
    per-``figure`` axis type (a construction-time argument), plotly's
    axis type can be set after the fact, so this needs no
    backend-specific construction-time wiring the way
    ``plotmux.backends.bokeh.backend._make_renderer`` does.

    A ``GridSpec`` cell is styled differently, per-subplot, by
    ``plotmux.backends.plotly.grid.render_grid`` (``update_xaxes``/
    ``update_yaxes`` with an explicit ``row``/``col``, and the title
    folded into ``make_subplots(subplot_titles=...)``, since plotly
    has only one figure-level ``title``): this function is not reused
    there.

    Args:
        fig: The plotly ``Figure`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The ``Figure`` that was styled.
    """
    layout: dict[str, Any] = {"xaxis_type": spec.xscale, "yaxis_type": spec.yscale}
    if spec.title is not None:
        layout["title"] = spec.title
    if spec.xlabel is not None:
        layout["xaxis_title"] = spec.xlabel
    if spec.ylabel is not None:
        layout["yaxis_title"] = spec.ylabel
    if spec.background_color is not None:
        layout["plot_bgcolor"] = rgba_to_plotly(
            cast("tuple[float, float, float, float]", spec.background_color)
        )
    # plotly's ``yaxis.range`` takes both bounds together (``[ymin,
    # ymax]``); unlike matplotlib's ``Axes.set_ylim``/bokeh's
    # ``y_range.start``/``.end``, there is no way to pin one bound and
    # leave the other autoscaled, so (same as
    # ``plotmux.backends.xy.style.apply_common_style``) only both
    # explicit bounds set together are forwarded.
    if spec.ymin is not None and spec.ymax is not None:
        layout["yaxis_range"] = [spec.ymin, spec.ymax]
    if spec.legend_title is not None:
        layout["legend_title_text"] = spec.legend_title
    fig.update_layout(**layout)
    return fig
