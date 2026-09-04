r"""Contain the backend-agnostic slope/abline annotation
specification."""

from __future__ import annotations

__all__ = ["SlopeSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import XBoundSpec

if TYPE_CHECKING:
    from plotmux.colors import Color


@dataclass(frozen=True)
class SlopeSpec(XBoundSpec):
    r"""Define a backend-agnostic slope (a.k.a. abline) annotation
    specification.

    Unlike ``LineSpec``, which is data-bound (an explicit ``x``/``y``
    pair), a ``SlopeSpec`` describes a line by its closed form,
    ``y = gradient * x + intercept``, spanning the current axes. It is
    the abstraction behind e.g. bokeh's ``bokeh.models.Slope`` and
    matplotlib's ``Axes.axline(slope=..., xy1=(0, intercept))``: a
    reference/trend line drawn without owning any data of its own. It
    typically appears as a ``plotmux.layer()`` child alongside a
    data-bound spec, e.g. a scatter plot with its fitted trend line
    overlaid: ``plotmux.layer(plotmux.scatter(x, y), SlopeSpec(gradient=2,
    intercept=10))``.

    Args:
        gradient: The line's slope.
        intercept: The line's y-intercept (the ``y`` value at
            ``x = 0``).
        label: An optional label used e.g. in the legend.
        color: An optional color for the line. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact semantics.
        linewidth: An optional line width. ``None`` uses the
            backend's default width.
        linestyle: The line's dash style.
        alpha: An optional line opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).

    Raises:
        ValueError: if ``alpha`` is not in ``[0, 1]``, or ``color``
            is not a valid color.

    Example:
        ```pycon
        >>> from plotmux.specs import SlopeSpec
        >>> spec = SlopeSpec(gradient=2, intercept=10)
        >>> spec.gradient
        2

        ```
    """

    gradient: float
    intercept: float = 0.0
    label: str | None = None
    color: Color = None
    linewidth: float | None = None
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid"
    alpha: float | None = None

    def __post_init__(self) -> None:
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        self._normalize_color()
        self._validate_base()
