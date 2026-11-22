r"""Contain xy-specific style helpers.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["LEGEND_LOCATION", "MARKERS", "apply_style", "rgba_to_xy"]

from typing import TYPE_CHECKING, Any

import xy

if TYPE_CHECKING:
    from plotmux.scene import AxesScene

#: The xy ``loc`` of each portable legend location.
LEGEND_LOCATION = {
    "top_left": "upper left",
    "top_right": "upper right",
    "bottom_left": "lower left",
    "bottom_right": "lower right",
    "top": "upper center",
    "bottom": "lower center",
    "left": "center left",
    "right": "center right",
}

#: The scatter markers drawn by xy (its ``symbol`` names).
MARKERS = ("circle", "square", "triangle", "diamond", "cross", "x")


def rgba_to_xy(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to xy's native CSS color string.

    xy's mark color parameters accept a CSS color string (e.g.
    ``"rgba(255, 0, 0, 1)"``), so the canonical ``[0, 1]`` float RGBA
    tuple of the scene is converted to that format here.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a CSS ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a``
            as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.xy.style import rgba_to_xy
        >>> rgba_to_xy((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"


def apply_style(chart: xy.Chart, scene: AxesScene) -> xy.Chart:
    r"""Apply the axes style of a scene onto an xy ``Chart``.

    xy charts are structure-immutable, so this builds a new ``Chart``
    instead of mutating ``chart``: the marks already drawn are kept
    and an ``x_axis``/``y_axis`` pair carrying the labels, the scales
    and the limits is appended, then a ``legend`` when the scene sets
    a legend title, location or orientation. The layout of ``chart``
    is copied over unchanged.

    ``xy.x_axis``/``xy.y_axis`` take both bounds of a limit together:
    a limit with only one explicit bound is left to the autoscale of
    xy.

    Args:
        chart: The xy ``Chart`` to style.
        scene: The scene whose axes style to apply.

    Returns:
        A new ``Chart`` with the axes style applied.

    Example:
        ```pycon
        >>> import numpy as np
        >>> import xy
        >>> from plotmux.backends.xy.style import apply_style
        >>> from plotmux.scene import AxesScene
        >>> chart = xy.chart(xy.line(np.arange(3.0), np.arange(3.0)))
        >>> apply_style(chart, AxesScene(primitives=(), title="t")).title
        't'

        ```
    """
    x_domain = _domain(scene.xlim)
    y_domain = _domain(scene.ylim)
    children = (
        *chart.children,
        xy.x_axis(label=scene.xlabel, type_=scene.xscale, domain=x_domain),
        xy.y_axis(label=scene.ylabel, type_=scene.yscale, domain=y_domain),
    )
    legend = scene.legend
    if legend is not None and (
        legend.title is not None or legend.location is not None or legend.orientation is not None
    ):
        legend_kwargs: dict[str, Any] = {
            "title": legend.title,
            "loc": None if legend.location is None else LEGEND_LOCATION[legend.location],
        }
        if legend.orientation == "horizontal":
            # xy has no orientation flag, only a column count: "horizontal"
            # lays out every named series in one row.
            named = sum(1 for child in chart.children if getattr(child, "name", None) is not None)
            legend_kwargs["ncols"] = max(named, 1)
        children = (*children, xy.legend(**legend_kwargs))
    style = dict(chart.style or {})
    if scene.background_color is not None:
        style["backgroundColor"] = rgba_to_xy(scene.background_color)
    return xy.Chart(
        chart.kind,
        children,
        title=scene.title,
        width=chart.width,
        height=chart.height,
        padding=chart.padding,
        data=chart.data,
        style=style or None,
    )


def _domain(limits: tuple[float | None, float | None]) -> tuple[float, float] | None:
    r"""Return the domain of an xy axis from the limits of a scene.

    Args:
        limits: The ``(lower, upper)`` limits of the scene.

    Returns:
        The ``(lower, upper)`` domain if both bounds are set, else
            ``None``: xy takes both bounds together.

    Example:
        ```pycon
        >>> from plotmux.backends.xy.style import _domain
        >>> _domain((1.0, 2.0))
        (1.0, 2.0)
        >>> _domain((1.0, None)) is None
        True

        ```
    """
    lower, upper = limits
    return (lower, upper) if lower is not None and upper is not None else None
