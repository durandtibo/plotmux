r"""Contain the backend-agnostic scatter-chart specification."""

from __future__ import annotations

__all__ = ["ScatterSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plotmux.colors import parse_color
from plotmux.specs.base import BaseSpec

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class ScatterSpec(BaseSpec):
    r"""Define a backend-agnostic scatter-chart specification.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the markers. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact semantics.
        size: An optional marker size. ``None`` uses the backend's
            default size.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``size`` is not a positive number, or ``color`` is not a
            valid color.

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
    label: str | None = None
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None
    size: float | None = None

    def __post_init__(self) -> None:
        if self.x.shape[0] != self.y.shape[0]:
            msg = (
                f"x and y must have the same length, but received "
                f"{self.x.shape[0]} and {self.y.shape[0]}"
            )
            raise ValueError(msg)
        if self.size is not None and self.size <= 0:
            msg = f"size must be a positive number, but received {self.size}"
            raise ValueError(msg)
        if self.color is not None:
            # Normalize to the canonical RGBA representation once, here,
            # so every backend receives an already-validated ``parse_color``
            # output and never has to parse a raw color itself.
            object.__setattr__(self, "color", parse_color(self.color))
