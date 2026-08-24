r"""Contain the backend-agnostic line-chart specification."""

from __future__ import annotations

__all__ = ["LineSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plotmux.specs.base import BaseSpec, _check_equal_length

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class LineSpec(BaseSpec):
    r"""Define a backend-agnostic line-chart specification.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the line. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact semantics.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            or ``color`` is not a valid color.

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
    label: str | None = None
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None

    def __post_init__(self) -> None:
        _check_equal_length(self.x, self.y)
        self._normalize_color()
