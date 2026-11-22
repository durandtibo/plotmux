r"""Apply the style of an ``AxesScene`` onto a plotly ``Figure``.

This module is only imported when plotly is installed (see
``plotmux.backends.plotly.__init__``), so it can import plotly
unconditionally.
"""

from __future__ import annotations

__all__ = [
    "DASH_STYLE",
    "LEGEND_LOCATION",
    "MARKER_STYLE",
    "apply_legend",
    "apply_style",
    "axis_range",
    "rgba_to_plotly",
]

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.scene import AxesScene

#: The plotly ``line.dash`` of each portable line style.
DASH_STYLE: dict[str, str] = {
    "solid": "solid",
    "dashed": "dash",
    "dotted": "dot",
    "dashdot": "dashdot",
}

#: The plotly marker symbol of each portable marker name.
MARKER_STYLE: dict[str, str] = {
    "circle": "circle",
    "square": "square",
    "triangle": "triangle-up",
    "diamond": "diamond",
    "cross": "cross",
    "x": "x",
}

#: The plotly ``legend`` layout of each portable legend location.
LEGEND_LOCATION: dict[str, dict[str, Any]] = {
    "top_left": {"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top"},
    "top_right": {"x": 0.99, "y": 0.99, "xanchor": "right", "yanchor": "top"},
    "bottom_left": {"x": 0.01, "y": 0.01, "xanchor": "left", "yanchor": "bottom"},
    "bottom_right": {"x": 0.99, "y": 0.01, "xanchor": "right", "yanchor": "bottom"},
    "top": {"x": 0.5, "y": 0.99, "xanchor": "center", "yanchor": "top"},
    "bottom": {"x": 0.5, "y": 0.01, "xanchor": "center", "yanchor": "bottom"},
    "left": {"x": 0.01, "y": 0.5, "xanchor": "left", "yanchor": "middle"},
    "right": {"x": 0.99, "y": 0.5, "xanchor": "right", "yanchor": "middle"},
}


def rgba_to_plotly(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to plotly's native color string.

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


def axis_range(limits: tuple[float | None, float | None], scale: str) -> list[float] | None:
    r"""Return the ``range`` of a plotly axis from the limits of a scene.

    plotly takes both bounds together, and the range of a log axis in
    powers of 10.

    Args:
        limits: The ``(lower, upper)`` limits of the scene.
        scale: ``"linear"`` or ``"log"``.

    Returns:
        The range if both bounds are set, else ``None`` (the axis is
            autoscaled).

    Example:
        ```pycon
        >>> from plotmux.backends.plotly.style import axis_range
        >>> axis_range((1.0, 100.0), "linear")
        [1.0, 100.0]
        >>> axis_range((1.0, 100.0), "log")
        [0.0, 2.0]
        >>> axis_range((1.0, None), "linear") is None
        True

        ```
    """
    lower, upper = limits
    if lower is None or upper is None:
        return None
    if scale == "log":
        return [math.log10(lower), math.log10(upper)]
    return [lower, upper]


def apply_style(
    fig: Figure, scene: AxesScene, *, row: int | None = None, col: int | None = None
) -> None:
    r"""Apply the axes style of a scene onto a plotly ``Figure``.

    The labels, the scales, the limits and the background are set on
    the axes of the subplot ``(row, col)``, or on the only axes of the
    figure when ``row`` and ``col`` are ``None``. plotly has one plot
    background per figure, so the background of a subplot is a
    rectangle drawn below its traces.

    Args:
        fig: The plotly ``Figure`` to style.
        scene: The scene whose axes style to apply.
        row: The 1-indexed subplot row, or ``None``.
        col: The 1-indexed subplot column, or ``None``.

    Example:
        ```pycon
        >>> import plotly.graph_objects as go
        >>> from plotmux.backends.plotly.style import apply_style
        >>> from plotmux.scene import AxesScene
        >>> fig = go.Figure()
        >>> apply_style(fig, AxesScene(primitives=(), xlabel="x"))
        >>> fig.layout.xaxis.title.text
        'x'

        ```
    """
    fig.update_xaxes(
        type=scene.xscale,
        title_text=scene.xlabel,
        range=axis_range(scene.xlim, scene.xscale),
        row=row,
        col=col,
    )
    fig.update_yaxes(
        type=scene.yscale,
        title_text=scene.ylabel,
        range=axis_range(scene.ylim, scene.yscale),
        row=row,
        col=col,
    )
    if scene.background_color is None:
        return
    color = rgba_to_plotly(scene.background_color)
    if row is None and col is None:
        fig.update_layout(plot_bgcolor=color)
    else:
        fig.add_shape(
            type="rect",
            xref="x domain",
            yref="y domain",
            x0=0,
            x1=1,
            y0=0,
            y1=1,
            fillcolor=color,
            line_width=0,
            layer="below",
            row=row,
            col=col,
        )


def apply_legend(fig: Figure, scene: AxesScene) -> None:
    r"""Apply the legend style of a scene onto a plotly ``Figure``.

    plotly has one legend per figure.

    Args:
        fig: The plotly ``Figure`` whose legend to style.
        scene: The scene whose legend style to apply.

    Example:
        ```pycon
        >>> import plotly.graph_objects as go
        >>> from plotmux.backends.plotly.style import apply_legend
        >>> from plotmux.scene import AxesScene, LegendStyle
        >>> fig = go.Figure()
        >>> apply_legend(fig, AxesScene(primitives=(), legend=LegendStyle(title="t")))
        >>> fig.layout.legend.title.text
        't'

        ```
    """
    if scene.legend is None:
        return
    legend: dict[str, Any] = {}
    if scene.legend.title is not None:
        legend["title"] = {"text": scene.legend.title}
    if scene.legend.location is not None:
        legend.update(LEGEND_LOCATION[scene.legend.location])
    if scene.legend.orientation is not None:
        legend["orientation"] = "h" if scene.legend.orientation == "horizontal" else "v"
    if legend:
        fig.update_layout(legend=legend)
