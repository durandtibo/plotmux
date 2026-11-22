r"""Contain the backend-agnostic bar-chart specification."""

from __future__ import annotations

__all__ = ["BarSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from plotmux.colors import parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Bars
from plotmux.specs.base import MarkSpec
from plotmux.utils.array import to_paired_arrays
from plotmux.utils.categorical import is_categorical
from plotmux.utils.extent import finite_extent

if TYPE_CHECKING:
    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class BarSpec(MarkSpec):
    r"""Define a backend-agnostic bar-chart mark.

    Args:
        x: The array of bar positions. Either numeric (evenly or
            unevenly spaced positions) or an array of strings, drawn
            as a categorical x-axis (e.g. ``x=["Apples", "Pears",
            "Nectarines"]``).
        y: The array of bar heights. Must have the same length as
            ``x``.
        width: The width of each bar, in ``x`` data units (a fraction
            of the band for a categorical ``x``). Must be a positive
            number.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``.

    Raises:
        InvalidSpecError: if ``x`` and ``y`` do not have the same
            length, ``width`` is not a positive number, or ``alpha`` is
            not in ``[0, 1]``. Also a ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import BarSpec
        >>> spec = BarSpec(x=np.arange(5), y=np.arange(5) ** 2)
        >>> spec.x.shape
        (5,)

        ```
    """

    x: np.ndarray
    y: np.ndarray
    width: float = 0.8

    def __post_init__(self) -> None:
        super().__post_init__()
        x, y = to_paired_arrays(self.x, self.y)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.width <= 0:
            msg = f"width must be a positive number, but received {self.width}"
            raise InvalidSpecError(msg)

    def x_extent(self) -> tuple[float, float] | None:
        return finite_extent(self.x, pad=self.width / 2)

    def is_categorical(self) -> bool | None:
        return is_categorical(self.x)

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        height = self.y.astype(float)
        return (
            Bars(
                x=self.x,
                height=height,
                base=np.zeros_like(height),
                width=self.width,
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                label=self.label,
            ),
        )
