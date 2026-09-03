r"""Contain the backend-agnostic histogram specification."""

from __future__ import annotations

__all__ = ["HistogramSpec"]

from dataclasses import dataclass, field
from numbers import Integral, Real

import numpy as np

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec


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
            See ``plotmux.utils.range.find_range`` for the exact
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
        alpha: An optional bar opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        title: An optional figure title. Inherited from ``BaseSpec``.
        xlabel: An optional x-axis label. Inherited from
            ``BaseSpec``.
        ylabel: An optional y-axis label. Inherited from
            ``BaseSpec``.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
            Inherited from ``BaseSpec``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
            Inherited from ``BaseSpec``.

    Raises:
        ValueError: if ``bins`` is not a positive integer, ``values``
            is not 1-dimensional or is empty, ``color`` is not a
            valid color, or ``xmin`` and ``xmax`` are both explicit
            numeric values with ``xmin >= xmax``.

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
    # ``kw_only=True``: ``BaseSpec`` also declares a plain, explicit-value-
    # only ``xmin``/``xmax`` pair (kw_only there too, see
    # ``plotmux.specs.base.BaseSpec``), and a same-named field redeclared
    # by a subclass keeps the *base* class's position in the dataclass's
    # generated ``__init__`` signature, not this class's -- without
    # ``kw_only=True`` here as well, that would reinsert this quantile-
    # capable ``xmin``/``xmax`` pair ahead of ``values`` (a required,
    # non-default field), breaking the dataclass's "no non-default field
    # after a default field" rule the same way ``BaseSpec``'s own kw-only
    # fields avoid it (see that class's module comment). Every call site
    # already passes ``xmin``/``xmax`` by keyword (``plotmux.hist(...,
    # xmin=...)``), so this changes no call site.
    #
    # This is a deliberate, narrower-typed shadow of ``BaseSpec.xmin``/
    # ``.xmax`` (``float | None``), not a Liskov violation in practice:
    # ``HistogramSpec``/``CdfSpec`` are never treated polymorphically
    # through a ``BaseSpec``-typed reference that then assigns a plain
    # ``float`` and reads back a ``str`` -- every reader goes through the
    # concrete subclass. Silenced rather than reshaped, per
    # ``DESIGN.md``'s 8.3 case study, which keeps this pair
    # quantile-capable and data-scoped, distinct from the plain,
    # explicit-value-only pair every other chart type gets from
    # ``BaseSpec``.
    xmin: float | str | None = field(default=None, kw_only=True)  # pyright: ignore[reportIncompatibleVariableOverride]
    xmax: float | str | None = field(default=None, kw_only=True)  # pyright: ignore[reportIncompatibleVariableOverride]
    label: str | None = None
    density: bool = False
    color: str | tuple[float, float, float] | tuple[float, float, float, float] | None = None
    alpha: float | None = None

    def __post_init__(self) -> None:
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        if not isinstance(self.bins, Integral) or isinstance(self.bins, bool) or self.bins <= 0:
            msg = f"bins must be a positive integer, but received {self.bins}"
            raise InvalidSpecError(msg)
        # Coerced with ``np.asarray`` so a spec can be constructed directly
        # (e.g. ``HistogramSpec(values=[1, 2, 3])``) and not only through
        # ``plotmux.hist``, which already converts its input before
        # construction (see ``plotmux.specs.base._check_equal_length``,
        # which does the same for ``LineSpec``/``ScatterSpec``).
        values = np.asarray(self.values)
        if values.ndim != 1:
            msg = f"values must be 1-dimensional, but received shape {values.shape}"
            raise InvalidSpecError(msg)
        if values.size == 0:
            msg = "values must not be empty"
            raise InvalidSpecError(msg)
        object.__setattr__(self, "values", values)
        # Only checked when both bounds are already explicit numbers: a
        # quantile string (e.g. "q0.1") or ``None`` is resolved against the
        # data later by ``find_range``, so it cannot be range-checked here.
        if isinstance(self.xmin, Real) and isinstance(self.xmax, Real) and self.xmin >= self.xmax:
            msg = (
                f"xmin must be strictly less than xmax, but received "
                f"xmin={self.xmin} and xmax={self.xmax}"
            )
            raise InvalidSpecError(msg)
        self._normalize_color()
        self._validate_base()
