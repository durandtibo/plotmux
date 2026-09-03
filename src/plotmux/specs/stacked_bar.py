r"""Contain the backend-agnostic stacked-bar-chart specification."""

from __future__ import annotations

__all__ = ["BarSeries", "StackedBarSpec"]

from dataclasses import dataclass, replace

import numpy as np

from plotmux.colors import parse_color
from plotmux.colors.palette import DEFAULT_PALETTE
from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec


@dataclass(frozen=True)
class BarSeries:
    r"""Define one series of a ``StackedBarSpec``.

    A small ``(y, label, color)`` tuple, mirroring how
    ``LayerSpec.layers`` holds a tuple of child specs -- see
    ``StackedBarSpec.series``.

    Args:
        y: The array of bar heights for this series. Must have the
            same length as the parent ``StackedBarSpec.x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for this series' bars. It can be a
            hex string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` gets a
            distinct color from ``plotmux.colors.palette.
            DEFAULT_PALETTE``, cycling in series order, the same way
            ``LayerSpec`` assigns default colors to its children (see
            ``plotmux.specs.layer._assign_default_colors``).

    Raises:
        ValueError: if ``color`` is not a valid color.
    """

    y: np.ndarray
    label: str | None = None
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class StackedBarSpec(BaseSpec):
    r"""Define a backend-agnostic stacked-bar-chart specification.

    Unlike ``layer()``'s ``BarSpec`` support (see
    ``plotmux.backends.matplotlib.layer`` and friends), which draws
    each child's bars independently onto shared axes with no
    coordination between them (several ``BarSpec``s at the same ``x``
    positions simply overlap), ``StackedBarSpec`` composes its
    ``series`` cumulatively: each series is drawn as a segment stacked
    on top of the running total of the series before it, at each
    ``x`` position, matching bokeh's ``vbar_stack``/matplotlib's own
    ``bottom=running_total`` idiom for a stacked bar (see DESIGN.md,
    section 8.4).

    Args:
        x: The array of bar positions, shared by every series. Either
            numeric or an array of strings, drawn as a categorical
            x-axis -- same semantics as ``BarSpec.x`` (see
            ``plotmux.utils.categorical.is_categorical``).
        series: The series to stack, in stacking order (bottom to
            top). Must be non-empty, and every series' ``y`` must have
            the same length as ``x``.
        width: The width of each bar, in ``x`` data units (categorical
            or numeric). Must be a positive number.
        alpha: An optional bar opacity, in ``[0, 1]``, applied to
            every series. ``None`` uses the backend's default (usually
            fully opaque).

    Raises:
        ValueError: if ``series`` is empty, any series' ``y`` does not
            have the same length as ``x``, ``width`` is not a positive
            number, ``alpha`` is not in ``[0, 1]``, or any series'
            ``color`` is not a valid color.

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
    alpha: float | None = None

    def __post_init__(self) -> None:
        x = np.asarray(self.x)
        if x.ndim != 1:
            msg = f"x must be 1-dimensional, but received shape {x.shape}"
            raise InvalidSpecError(msg)
        object.__setattr__(self, "x", x)
        if not self.series:
            msg = "series must contain at least one BarSeries"
            raise InvalidSpecError(msg)
        normalized = []
        i = 0
        for s in self.series:
            y = np.asarray(s.y)
            if y.ndim != 1 or y.shape[0] != x.shape[0]:
                msg = (
                    f"each series' y must have the same length as x, but received "
                    f"x length {x.shape[0]} and y shape {y.shape}"
                )
                raise InvalidSpecError(msg)
            color = s.color
            if color is None:
                color = DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]
                i += 1
            else:
                color = parse_color(color)
            normalized.append(replace(s, y=y, color=color))
        object.__setattr__(self, "series", tuple(normalized))
        if self.width <= 0:
            msg = f"width must be a positive number, but received {self.width}"
            raise InvalidSpecError(msg)
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        self._validate_base()
