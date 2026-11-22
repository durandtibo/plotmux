r"""Contain the backend-agnostic scatter-chart specification."""

from __future__ import annotations

__all__ = ["ScatterSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from plotmux.colors import Color, parse_color, parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Points
from plotmux.specs.base import MarkSpec
from plotmux.utils.array import to_paired_arrays
from plotmux.utils.categorical import is_categorical
from plotmux.utils.extent import finite_extent
from plotmux.utils.finite import check_no_inf

if TYPE_CHECKING:
    import numpy as np

    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class ScatterSpec(MarkSpec):
    r"""Define a backend-agnostic scatter mark.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        size: An optional marker size. ``None`` uses the backend's
            default size.
        edgecolor: An optional, separate color for the marker edge
            (as opposed to ``color``, which fills the marker). Same
            format as ``color``. ``None`` uses ``color`` for the edge
            too.
        marker: An optional marker shape, one of a small,
            backend-portable set. ``None`` uses the backend's default
            shape (a circle on every backend).
        fill: An optional tri-state fill toggle. ``None``/``True``
            draw a filled marker using ``color``. ``False`` draws a
            hollow marker: only the outline (``edgecolor`` if set,
            else ``color``) is drawn.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``. ``NaN`` values are kept (no point). ``inf`` and
    ``-inf`` values are rejected.

    Raises:
        InvalidSpecError: if ``x`` and ``y`` do not have the same
            length, ``x`` or ``y`` has an infinite value, ``size`` is
            not a positive number, or ``alpha`` is not in ``[0, 1]``. Also
            a ``ValueError``.
        InvalidColorError: if ``color``/``edgecolor`` is not a valid
            color. Also a ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import ScatterSpec
        >>> spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
        >>> spec.x.shape
        (10,)

        ```
    """

    x: np.ndarray
    y: np.ndarray
    size: float | None = None
    edgecolor: Color = None
    marker: Literal["circle", "square", "triangle", "diamond", "cross", "x"] | None = None
    fill: bool | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        x, y = to_paired_arrays(self.x, self.y)
        check_no_inf(x, owner="ScatterSpec", name="x")
        check_no_inf(y, owner="ScatterSpec", name="y")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.size is not None and self.size <= 0:
            msg = f"size must be a positive number, but received {self.size}"
            raise InvalidSpecError(msg)
        if self.edgecolor is not None:
            object.__setattr__(self, "edgecolor", parse_color(self.edgecolor))

    def x_extent(self) -> tuple[float, float] | None:
        return finite_extent(self.x)

    def is_categorical(self) -> bool | None:
        return is_categorical(self.x)

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        return (
            Points(
                x=self.x,
                y=self.y,
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                size=self.size,
                marker=self.marker,
                fill=self.fill,
                edgecolor=parse_optional_color(self.edgecolor),
                label=self.label,
            ),
        )
