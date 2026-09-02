r"""Contain the backend-agnostic bar-chart specification."""

from __future__ import annotations

__all__ = ["BarSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec, _check_equal_length

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class BarSpec(BaseSpec):
    r"""Define a backend-agnostic bar-chart specification.

    Args:
        x: The array of bar positions.
        y: The array of bar heights. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the bars. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact semantics.
        width: The width of each bar, in ``x`` data units. Must be a
            positive number.
        alpha: An optional bar opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``width`` is not a positive number, ``alpha`` is not in
            ``[0, 1]``, or ``color`` is not a valid color.

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
    label: str | None = None
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None
    width: float = 0.8
    alpha: float | None = None

    def __post_init__(self) -> None:
        x, y = _check_equal_length(self.x, self.y)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.width <= 0:
            msg = f"width must be a positive number, but received {self.width}"
            raise InvalidSpecError(msg)
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        self._normalize_color()
        self._validate_base()
