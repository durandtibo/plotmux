r"""Contain the backend-agnostic histogram specification."""

from __future__ import annotations

__all__ = ["HistogramSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plotmux.colors import parse_color
from plotmux.specs.base import BaseSpec

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class HistogramSpec(BaseSpec):
    r"""Define a backend-agnostic histogram specification.

    Args:
        values: The array of values to plot.
        bins: The number of histogram bins. Must be a positive
            integer.
        xmin: Specifies the lower bound of the x-axis range. It can
            be an explicit value, a quantile string such as
            ``"q0.1"``, or ``None`` to use the minimum of ``values``.
            See ``plotmux.core.range.find_range`` for the exact
            semantics.
        xmax: Specifies the upper bound of the x-axis range. Same
            semantics as ``xmin`` but for the upper bound.
        label: An optional label used e.g. in the legend.
        density: If ``True``, draw and return a probability
            density: each bin will display the bin's raw count
            divided by the total number of counts and the bin
            width, so that the area under the histogram integrates
            to 1. Defaults to ``False``.
        color: An optional color for the bars. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact
            semantics.

    Raises:
        ValueError: if ``bins`` is not a positive integer or
            ``color`` is not a valid color.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import HistogramSpec
        >>> spec = HistogramSpec(values=np.arange(101), bins=10)
        >>> spec.bins
        10

        ```
    """

    values: np.ndarray
    bins: int = 30
    xmin: float | str | None = None
    xmax: float | str | None = None
    label: str | None = None
    density: bool = False
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None

    def __post_init__(self) -> None:
        if self.bins <= 0:
            msg = f"bins must be a positive integer, but received {self.bins}"
            raise ValueError(msg)
        if self.color is not None:
            # Normalize to the canonical RGBA representation once, here,
            # so every backend receives an already-validated ``parse_color``
            # output and never has to parse a raw color itself.
            object.__setattr__(self, "color", parse_color(self.color))
