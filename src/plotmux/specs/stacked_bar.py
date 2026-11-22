r"""Contain the backend-agnostic stacked-bar-chart specification."""

from __future__ import annotations

__all__ = ["BarSeries", "StackedBarSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from plotmux.colors import Color, parse_color, parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Bars
from plotmux.specs.base import MarkSpec, Spec
from plotmux.utils.array import to_readonly_array
from plotmux.utils.categorical import is_categorical
from plotmux.utils.extent import finite_extent

if TYPE_CHECKING:
    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class BarSeries(Spec):
    r"""Define one series of a ``StackedBarSpec``.

    Args:
        y: The array of bar heights for this series. Must have the
            same length as the parent ``StackedBarSpec.x``.
        label: An optional label used in the legend.
        color: An optional color for this series' bars. It can be a
            hex string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` takes the
            next color of ``plotmux.colors.palette.DEFAULT_PALETTE``
            (see ``plotmux.scene.build_scene``).

    Raises:
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import BarSeries
        >>> BarSeries(y=np.arange(3), label="a").y.shape
        (3,)

        ```
    """

    y: np.ndarray
    label: str | None = None
    color: Color = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "y", to_readonly_array(self.y))
        if self.color is not None:
            object.__setattr__(self, "color", parse_color(self.color))


@dataclass(frozen=True, eq=False)
class StackedBarSpec(MarkSpec):
    r"""Define a backend-agnostic stacked-bar-chart mark.

    Each series is a segment stacked on top of the running total of the
    series before it, at each ``x`` position. The running total is a
    plain cumulative sum (negative values are not handled specially).

    Args:
        x: The array of bar positions, shared by every series. Either
            numeric or an array of strings, drawn as a categorical
            x-axis, same semantics as ``BarSpec.x``.
        series: The series to stack, in stacking order (bottom to
            top). Must be non-empty, and every series' ``y`` must have
            the same length as ``x``.
        width: The width of each bar, in ``x`` data units (a fraction
            of the band for a categorical ``x``). Must be a positive
            number.

    ``alpha`` is inherited from ``MarkSpec`` and applies to every
    series. The label and the color are set on each ``BarSeries``,
    not on the spec.

    Raises:
        InvalidSpecError: if ``series`` is empty, any series' ``y``
            does not have the same length as ``x``, ``width`` is not a
            positive number, ``alpha`` is not in ``[0, 1]``, or
            ``label`` or ``color`` is set on the spec. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import BarSeries, StackedBarSpec
        >>> spec = StackedBarSpec(
        ...     x=np.array(["Apples", "Pears", "Nectarines"]),
        ...     series=(
        ...         BarSeries(y=np.array([2, 1, 4]), label="2015"),
        ...         BarSeries(y=np.array([1, 3, 2]), label="2016"),
        ...     ),
        ... )
        >>> len(spec.series)
        2

        ```
    """

    x: np.ndarray
    series: tuple[BarSeries, ...]
    width: float = 0.8

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.label is not None or self.color is not None:
            msg = "label and color must be set on each BarSeries, not on the StackedBarSpec"
            raise InvalidSpecError(msg)
        x = to_readonly_array(self.x)
        if x.ndim != 1:
            msg = f"x must be 1-dimensional, but received shape {x.shape}"
            raise InvalidSpecError(msg)
        object.__setattr__(self, "x", x)
        series = tuple(self.series)
        if not series:
            msg = "series must contain at least one BarSeries"
            raise InvalidSpecError(msg)
        for s in series:
            if s.y.ndim != 1 or s.y.shape[0] != x.shape[0]:
                msg = (
                    f"each series' y must have the same length as x, but received "
                    f"x length {x.shape[0]} and y shape {s.y.shape}"
                )
                raise InvalidSpecError(msg)
        object.__setattr__(self, "series", series)
        if self.width <= 0:
            msg = f"width must be a positive number, but received {self.width}"
            raise InvalidSpecError(msg)

    def x_extent(self) -> tuple[float, float] | None:
        return finite_extent(self.x, pad=self.width / 2)

    def is_categorical(self) -> bool | None:
        return is_categorical(self.x)

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        primitives = []
        base = np.zeros(self.x.shape[0])
        for s in self.series:
            height = s.y.astype(float)
            primitives.append(
                Bars(
                    x=self.x,
                    height=height,
                    base=base,
                    width=self.width,
                    color=parse_optional_color(s.color),
                    alpha=self.alpha,
                    label=s.label,
                )
            )
            base = base + height
        return tuple(primitives)
