r"""Apply the style of an ``AxesScene`` onto a bokeh ``figure``.

This module is only imported when bokeh is installed (see
``plotmux.backends.bokeh.__init__``), so it can import bokeh
unconditionally.
"""

from __future__ import annotations

__all__ = ["LEGEND_LOCATIONS", "MARKERS", "apply_style", "rgba_to_bokeh"]

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from bokeh.models import DataRange1d
    from bokeh.plotting import figure

    from plotmux.scene import AxesScene

#: The portable legend locations, which bokeh accepts as they are.
LEGEND_LOCATIONS = (
    "top_left",
    "top_right",
    "bottom_left",
    "bottom_right",
    "top",
    "bottom",
    "left",
    "right",
)

#: The scatter markers drawn by bokeh (its ``marker`` names).
MARKERS = ("circle", "square", "triangle", "diamond", "cross", "x")


def rgba_to_bokeh(color: tuple[float, float, float, float]) -> tuple[int, int, int, float]:
    r"""Convert a canonical RGBA tuple to bokeh's native color tuple.

    bokeh's glyph color parameters (e.g. ``line_color``, ``fill_color``)
    accept an ``(r, g, b, a)`` tuple with ``r``/``g``/``b`` as integers
    in ``[0, 255]``.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as an ``(r, g, b, a)`` tuple, with ``r``/``g``/``b`` as
            integers in ``[0, 255]`` and ``a`` as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.bokeh.style import rgba_to_bokeh
        >>> rgba_to_bokeh((1.0, 0.0, 0.0, 1.0))
        (255, 0, 0, 1.0)

        ```
    """
    r, g, b, a = color
    return (round(r * 255), round(g * 255), round(b * 255), a)


def apply_style(fig: figure, scene: AxesScene) -> figure:
    r"""Apply the axes style of a scene onto a bokeh ``figure``.

    It applies the title, the axis labels, the background color, the
    limits and the legend. The axis scales are not set here: they are
    construction-time arguments of ``bokeh.plotting.figure`` (see
    ``plotmux.backends.bokeh.backend``).

    Args:
        fig: The bokeh ``figure`` to style.
        scene: The scene whose axes style to apply.

    Returns:
        The ``figure`` that was styled.

    Example:
        ```pycon
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.style import apply_style
        >>> from plotmux.scene import AxesScene
        >>> apply_style(figure(), AxesScene(primitives=(), title="t")).title.text
        't'

        ```
    """
    if scene.title is not None:
        fig.title = scene.title
    if scene.xlabel is not None:
        fig.xaxis.axis_label = scene.xlabel
    if scene.ylabel is not None:
        fig.yaxis.axis_label = scene.ylabel
    if scene.background_color is not None:
        fig.background_fill_color = rgba_to_bokeh(scene.background_color)
    if scene.categories is None:
        x_range = cast("DataRange1d", fig.x_range)
        if scene.xlim[0] is not None:
            x_range.start = scene.xlim[0]
        if scene.xlim[1] is not None:
            x_range.end = scene.xlim[1]
    y_range = cast("DataRange1d", fig.y_range)
    if scene.ylim[0] is not None:
        y_range.start = scene.ylim[0]
    if scene.ylim[1] is not None:
        y_range.end = scene.ylim[1]
    _apply_legend(fig, scene)
    return fig


def _apply_legend(fig: figure, scene: AxesScene) -> None:
    r"""Apply the legend style of a scene onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` whose legend to style.
        scene: The scene whose legend style to apply.

    Example:
        ```pycon
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.style import _apply_legend
        >>> from plotmux.scene import AxesScene
        >>> _apply_legend(figure(), AxesScene(primitives=()))

        ```
    """
    if scene.legend is None or not fig.legend:
        return
    if scene.legend.title is not None:
        fig.legend.title = scene.legend.title
    if scene.legend.location is not None:
        fig.legend.location = scene.legend.location
    if scene.legend.orientation is not None:
        fig.legend.orientation = scene.legend.orientation
