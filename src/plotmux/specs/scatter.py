r"""Contain the backend-agnostic scatter-chart specification."""

from __future__ import annotations

__all__ = ["ScatterSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import XBoundSpec, check_equal_length

if TYPE_CHECKING:
    import numpy as np

    from plotmux.colors import Color


@dataclass(frozen=True)
class ScatterSpec(XBoundSpec):
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
        edgecolor: An optional, separate color for the marker edge
            (as opposed to ``color``, which fills the marker). Same
            format as ``color``. ``None`` uses ``color`` for the edge
            too (every backend's renderer already does this when
            ``edgecolor`` is unset -- see e.g.
            ``plotmux.backends.bokeh.scatter.render_scatter``), so a
            plain, single-color marker still needs only ``color``.
        alpha: An optional marker opacity, in ``[0, 1]``. ``None``
            uses the backend's default (usually fully opaque).
        marker: An optional marker shape, one of a small,
            backend-portable set (mirroring how ``LineSpec.linestyle``
            exposes four portable names rather than every backend's
            native dash vocabulary). ``None`` uses the backend's
            default shape (a circle on every current backend). altair
            has no native ``"x"`` shape (see
            ``plotmux.backends.altair.style.MARKER_STYLE``), a small,
            permanent per-backend asymmetry, the same pattern as
            ``BarSpec.width``'s altair gap.
        fill: An optional tri-state fill toggle. ``None``/``True``
            draw a filled marker using ``color``, today's behavior.
            ``False`` draws a hollow marker: only the outline (
            ``edgecolor`` if set, else ``color``) is drawn, with no
            fill -- distinct from leaving ``color`` unset, which asks
            for the backend's own default (opaque) fill color rather
            than an explicitly transparent one. Every current
            backend's own default fill is opaque, so ``fill=False``
            is the only portable way to get a hollow marker.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``size`` is not a positive number, ``alpha`` is not in
            ``[0, 1]``, or ``color``/``edgecolor`` is not a valid
            color.

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
    color: Color = None
    size: float | None = None
    edgecolor: Color = None
    alpha: float | None = None
    marker: Literal["circle", "square", "triangle", "diamond", "cross", "x"] | None = None
    fill: bool | None = None

    def __post_init__(self) -> None:
        x, y = check_equal_length(self.x, self.y)
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.size is not None and self.size <= 0:
            msg = f"size must be a positive number, but received {self.size}"
            raise InvalidSpecError(msg)
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        self._normalize_color()
        self._normalize_color("edgecolor")
        self._validate_base()
