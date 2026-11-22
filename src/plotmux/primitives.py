r"""Contain the three drawing primitives a backend has to draw.

The core lowers every mark to ``Bars``, ``Line`` or ``Points`` (see
``plotmux.specs.MarkSpec.to_primitives``), so a backend only translates
these three primitives, and every backend draws the same numbers.
"""

from __future__ import annotations

__all__ = ["RGBA", "Bars", "Line", "Points", "Primitive"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from plotmux.utils.equality import ValueObject

if TYPE_CHECKING:
    import numpy as np

RGBA: TypeAlias = tuple[float, float, float, float]


@dataclass(frozen=True, eq=False)
class Bars(ValueObject):
    r"""Define a set of vertical bars (histogram, bar chart, one series
    of a stacked bar chart).

    Args:
        x: The bar centers (floats), or the categories (strings).
        height: The bar heights, from ``base`` to ``base + height``.
        base: The bar bases: zeros, or the running total of a stacked
            bar.
        width: The bar width in data units, one value for every bar
            or an array with one value per bar. The fraction of the
            band when ``x`` is categorical.
        color: The bar color. ``None`` only before ``build_scene``
            gives it a palette color.
        alpha: The bar opacity, or ``None`` for the default.
        label: The legend label, or ``None``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.primitives import Bars
        >>> bars = Bars(x=np.arange(3.0), height=np.ones(3), base=np.zeros(3), width=0.8)
        >>> bars.width
        0.8

        ```
    """

    x: np.ndarray
    height: np.ndarray
    base: np.ndarray
    width: float | np.ndarray
    color: RGBA | None = None
    alpha: float | None = None
    label: str | None = None


@dataclass(frozen=True, eq=False)
class Line(ValueObject):
    r"""Define a polyline (line chart, CDF steps, slope).

    Args:
        x: The x vertices.
        y: The y vertices. ``NaN`` is a gap.
        infinite: The ``(gradient, intercept)`` of a slope, ``None``
            for any other line. A backend with a native infinite line
            may draw it instead of the segment ``x``, ``y``.
        color: The line color. ``None`` only before ``build_scene``
            gives it a palette color.
        alpha: The line opacity, or ``None`` for the default.
        linewidth: The line width, or ``None`` for the default.
        linestyle: ``"solid"``, ``"dashed"``, ``"dotted"`` or
            ``"dashdot"``.
        label: The legend label, or ``None``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.primitives import Line
        >>> Line(x=np.arange(3.0), y=np.arange(3.0)).linestyle
        'solid'

        ```
    """

    x: np.ndarray
    y: np.ndarray
    infinite: tuple[float, float] | None = None
    color: RGBA | None = None
    alpha: float | None = None
    linewidth: float | None = None
    linestyle: str = "solid"
    label: str | None = None


@dataclass(frozen=True, eq=False)
class Points(ValueObject):
    r"""Define a set of markers (scatter chart).

    Args:
        x: The x positions.
        y: The y positions. ``NaN`` is a missing point.
        color: The marker fill color. ``None`` only before
            ``build_scene`` gives it a palette color.
        alpha: The marker opacity, or ``None`` for the default.
        size: The marker size, or ``None`` for the default.
        marker: The marker shape, or ``None`` for a circle.
        fill: ``False`` for a hollow marker, ``None`` or ``True`` for a
            filled one.
        edgecolor: The marker edge color, or ``None`` to use ``color``.
        label: The legend label, or ``None``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.primitives import Points
        >>> Points(x=np.arange(3.0), y=np.arange(3.0)).marker is None
        True

        ```
    """

    x: np.ndarray
    y: np.ndarray
    color: RGBA | None = None
    alpha: float | None = None
    size: float | None = None
    marker: str | None = None
    fill: bool | None = None
    edgecolor: RGBA | None = None
    label: str | None = None


Primitive: TypeAlias = Bars | Line | Points
