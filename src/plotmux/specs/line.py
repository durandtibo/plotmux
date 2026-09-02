r"""Contain the backend-agnostic line-chart specification."""

from __future__ import annotations

__all__ = ["LineSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from plotmux.exceptions import InvalidSpecError
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
        alpha: An optional line opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        linewidth: An optional line width. ``None`` uses the
            backend's default width. Same field name/semantics as
            ``SlopeSpec.linewidth``.
        linestyle: The line's dash style. Same field name/semantics
            as ``SlopeSpec.linestyle``.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``alpha`` is not in ``[0, 1]``, or ``color`` is not a
            valid color.

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
    alpha: float | None = None
    linewidth: float | None = None
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid"

    def __post_init__(self) -> None:
        x, y = _check_equal_length(self.x, self.y)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        self._normalize_color()
        self._validate_base()
