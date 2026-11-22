r"""Contain the scene: the spec of a figure lowered to drawing
primitives.

``build_scene`` owns every decision that changes the numbers on the
screen (ranges, bins, steps, stacking, default colors, extents). A
backend only translates the three primitives (``Bars``, ``Line``,
``Points``) and the axes style of an ``AxesScene`` into one library,
so it cannot draw a different histogram than another backend.
"""

from __future__ import annotations

__all__ = [
    "AxesScene",
    "Bars",
    "GridScene",
    "LegendStyle",
    "Line",
    "Points",
    "build_scene",
]

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal, overload

from plotmux.colors import parse_optional_color
from plotmux.colors.palette import DEFAULT_PALETTE
from plotmux.primitives import Bars, Line, Points
from plotmux.specs import GridSpec, PanelSpec
from plotmux.utils.equality import ValueObject

if TYPE_CHECKING:
    from plotmux.primitives import RGBA, Primitive
    from plotmux.specs import FigureSpec, LegendLocation


@dataclass(frozen=True, eq=False)
class LegendStyle(ValueObject):
    r"""Define the style of the legend of an axes.

    Args:
        title: The heading of the legend box, or ``None``.
        location: The legend position, or ``None`` for the backend's
            default.
        orientation: The legend layout, or ``None`` for the backend's
            default.

    Example:
        ```pycon
        >>> from plotmux.scene import LegendStyle
        >>> LegendStyle(title="t").location is None
        True

        ```
    """

    title: str | None = None
    location: LegendLocation | None = None
    orientation: Literal["vertical", "horizontal"] | None = None


@dataclass(frozen=True, eq=False)
class AxesScene(ValueObject):
    r"""Define the lowered description of one axes.

    Args:
        primitives: The primitives to draw, in drawing order. Every
            primitive has a color.
        title: The axes title, or ``None``.
        xlabel: The x-axis label, or ``None``.
        ylabel: The y-axis label, or ``None``.
        xscale: ``"linear"`` or ``"log"``.
        yscale: ``"linear"`` or ``"log"``.
        xlim: The ``(lower, upper)`` x limits, each ``None`` to
            autoscale.
        ylim: The ``(lower, upper)`` y limits, each ``None`` to
            autoscale.
        background_color: The axes background color, or ``None``.
        legend: The legend style, ``None`` when no primitive has a
            label (there is no legend).
        categories: The categories of a categorical x-axis, in order
            of first appearance, or ``None`` for a numeric x-axis.
    """

    primitives: tuple[Primitive, ...]
    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    xscale: Literal["linear", "log"] = "linear"
    yscale: Literal["linear", "log"] = "linear"
    xlim: tuple[float | None, float | None] = (None, None)
    ylim: tuple[float | None, float | None] = (None, None)
    background_color: RGBA | None = None
    legend: LegendStyle | None = None
    categories: tuple[str, ...] | None = None


@dataclass(frozen=True, eq=False)
class GridScene(ValueObject):
    r"""Define the lowered description of a grid of axes.

    Args:
        panels: The axes, in row-major order.
        ncols: The number of columns.
        title: The title of the whole grid, or ``None``.
    """

    panels: tuple[AxesScene, ...]
    ncols: int = 1
    title: str | None = None


@overload
def build_scene(spec: PanelSpec) -> AxesScene: ...
@overload
def build_scene(spec: GridSpec) -> GridScene: ...
def build_scene(spec: FigureSpec) -> AxesScene | GridScene:
    r"""Lower the spec of a figure to a scene.

    It is a pure function of the spec: the same spec gives an equal
    scene.

    1. The x extent of each panel is resolved (``PanelSpec.x_extent``).
    2. Each mark is lowered to primitives (``MarkSpec.to_primitives``),
       in order.
    3. Each primitive with no color gets the next color of
       ``DEFAULT_PALETTE``, cycling in drawing order. A primitive with
       an explicit color does not consume a color, and the first
       primitive of a single mark gets one too, so the swap of the
       backend does not change the color.
    4. The legend exists if and only if one primitive has a label.
    5. The categories are collected in order of first appearance.

    Args:
        spec: The spec of a panel or of a grid.

    Returns:
        An ``AxesScene`` for a ``PanelSpec``, a ``GridScene`` for a
            ``GridSpec``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.scene import build_scene
        >>> from plotmux.specs import LineSpec, PanelSpec
        >>> scene = build_scene(PanelSpec(marks=(LineSpec(x=np.arange(3), y=np.arange(3)),)))
        >>> scene.primitives[0].color
        (0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0)

        ```
    """
    if isinstance(spec, GridSpec):
        return GridScene(
            panels=tuple(_build_axes(panel) for panel in spec.panels),
            ncols=spec.ncols,
            title=spec.title,
        )
    return _build_axes(spec)


def _build_axes(panel: PanelSpec) -> AxesScene:
    r"""Lower one panel to an ``AxesScene``.

    Args:
        panel: The panel to lower.

    Returns:
        The scene of the panel.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.scene import _build_axes
        >>> from plotmux.specs import LineSpec, PanelSpec
        >>> _build_axes(PanelSpec(marks=(LineSpec(x=np.arange(3), y=np.arange(3)),))).legend is None
        True

        ```
    """
    extent = panel.x_extent()
    primitives = _assign_colors(
        tuple(p for mark in panel.marks for p in mark.to_primitives(extent))
    )
    legend = None
    if any(p.label is not None for p in primitives):
        legend = LegendStyle(
            title=panel.legend_title,
            location=panel.legend_location,
            orientation=panel.legend_orientation,
        )
    return AxesScene(
        primitives=primitives,
        title=panel.title,
        xlabel=panel.xlabel,
        ylabel=panel.ylabel,
        xscale=panel.xscale,
        yscale=panel.yscale,
        xlim=(panel.xmin, panel.xmax),
        ylim=(panel.ymin, panel.ymax),
        background_color=parse_optional_color(panel.background_color),
        legend=legend,
        categories=_collect_categories(primitives),
    )


def _assign_colors(primitives: tuple[Primitive, ...]) -> tuple[Primitive, ...]:
    r"""Give a palette color to each primitive that has none.

    The palette cycles in drawing order. A primitive with an explicit
    color does not consume a slot.

    Args:
        primitives: The primitives to color.

    Returns:
        The same primitives, in the same order, each with a color.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.primitives import Line
        >>> from plotmux.scene import _assign_colors
        >>> line = Line(x=np.arange(2.0), y=np.arange(2.0))
        >>> _assign_colors((line, line))[1].color == _assign_colors((line, line))[0].color
        False

        ```
    """
    result: list[Primitive] = []
    index = 0
    for primitive in primitives:
        if primitive.color is None:
            primitive = replace(primitive, color=DEFAULT_PALETTE[index % len(DEFAULT_PALETTE)])  # noqa: PLW2901
            index += 1
        result.append(primitive)
    return tuple(result)


def _collect_categories(primitives: tuple[Primitive, ...]) -> tuple[str, ...] | None:
    r"""Collect the categories of the x-axis, in order of first
    appearance.

    Args:
        primitives: The primitives of the axes.

    Returns:
        The distinct categories, or ``None`` if the x-axis is not
            categorical.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.primitives import Bars
        >>> from plotmux.scene import _collect_categories
        >>> bars = Bars(
        ...     x=np.array(["b", "a", "b"]), height=np.ones(3), base=np.zeros(3), width=0.8
        ... )
        >>> _collect_categories((bars,))
        ('b', 'a')

        ```
    """
    categories: dict[str, None] = {}
    for primitive in primitives:
        if primitive.x.dtype.kind in "US":
            categories.update(dict.fromkeys(primitive.x.astype(str).tolist()))
    return tuple(categories) or None
