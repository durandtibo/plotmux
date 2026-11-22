r"""Contain the backend-agnostic line-chart specification."""

from __future__ import annotations

__all__ = ["LineSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from plotmux.colors import parse_optional_color
from plotmux.primitives import Line
from plotmux.specs.base import MarkSpec
from plotmux.utils.array import to_paired_arrays
from plotmux.utils.categorical import is_categorical
from plotmux.utils.extent import finite_extent
from plotmux.utils.finite import check_no_inf

if TYPE_CHECKING:
    import numpy as np

    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class LineSpec(MarkSpec):
    r"""Define a backend-agnostic line mark.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        linewidth: An optional line width. ``None`` uses the
            backend's default width.
        linestyle: The line's dash style.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``. ``NaN`` values are kept (a gap in the line).
    ``inf`` and ``-inf`` values are rejected.

    Raises:
        InvalidSpecError: if ``x`` and ``y`` do not have the same
            length, ``x`` or ``y`` has an infinite value, or ``alpha`` is
            not in ``[0, 1]``. Also a ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import LineSpec
        >>> spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
        >>> spec.x.shape
        (10,)

        ```
    """

    x: np.ndarray
    y: np.ndarray
    linewidth: float | None = None
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid"

    def __post_init__(self) -> None:
        super().__post_init__()
        x, y = to_paired_arrays(self.x, self.y)
        check_no_inf(x, owner="LineSpec", name="x")
        check_no_inf(y, owner="LineSpec", name="y")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def x_extent(self) -> tuple[float, float] | None:
        return finite_extent(self.x)

    def is_categorical(self) -> bool | None:
        return is_categorical(self.x)

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        return (
            Line(
                x=self.x,
                y=self.y,
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                linewidth=self.linewidth,
                linestyle=self.linestyle,
                label=self.label,
            ),
        )
