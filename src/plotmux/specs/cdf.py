r"""Contain the backend-agnostic empirical CDF specification."""

from __future__ import annotations

__all__ = ["CdfSpec"]

from dataclasses import dataclass, field
from numbers import Integral, Real
from typing import TYPE_CHECKING

import numpy as np

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec

if TYPE_CHECKING:
    from plotmux.colors import Color


@dataclass(frozen=True)
class CdfSpec(BaseSpec):
    r"""Define a backend-agnostic empirical cumulative distribution
    function (CDF) specification.

    Args:
        values: The array of values to plot.
        nbins: The number of bins to use to approximate the
            cumulative distribution. Must be a positive integer, or
            ``None`` to use the backend's default binning.
        xmin: Specifies the lower bound of the x-axis range. It can
            be an explicit value, a quantile string such as
            ``"q0.1"``, or ``None`` to use the minimum of ``values``.
            See ``plotmux.utils.range.find_range`` for the exact
            semantics.
        xmax: Specifies the upper bound of the x-axis range. Same
            semantics as ``xmin`` but for the upper bound.
        label: An optional label used e.g. in the legend.
        color: An optional color for the curve. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color. See
            ``plotmux.colors.parse_color`` for the exact
            semantics.
        alpha: An optional curve opacity, in ``[0, 1]``. ``None``
            uses the backend's default (usually fully opaque).
        title: An optional figure title. Inherited from ``BaseSpec``.
        xlabel: An optional x-axis label. Inherited from
            ``BaseSpec``.
        ylabel: An optional y-axis label. Defaults to
            ``"cumulative probability"`` rather than ``BaseSpec``'s
            usual ``None``, since a CDF's y-axis always represents
            that same quantity unless the caller overrides it.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
            Inherited from ``BaseSpec``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
            Inherited from ``BaseSpec``.

    Raises:
        ValueError: if ``nbins`` is set and is not a positive
            integer, ``values`` is not 1-dimensional or is empty,
            ``color`` is not a valid color, or ``xmin`` and ``xmax``
            are both explicit numeric values with ``xmin >= xmax``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import CdfSpec
        >>> spec = CdfSpec(values=np.arange(101), nbins=10)
        >>> spec.nbins
        10

        ```
    """

    values: np.ndarray
    nbins: int | None = None
    # ``kw_only=True``: see ``HistogramSpec.xmin``/``.xmax``'s matching
    # comment -- ``BaseSpec`` also declares a same-named, kw-only pair,
    # and without ``kw_only=True`` here too this quantile-capable
    # redeclaration would keep ``BaseSpec``'s field position (ahead of
    # ``values``), breaking dataclass field ordering. ``BaseSpec.xmin``/
    # ``xmax`` are typed ``float | str | None`` for the same reason,
    # so this override needs no widening of its own.
    xmin: float | str | None = field(default=None, kw_only=True)
    xmax: float | str | None = field(default=None, kw_only=True)
    label: str | None = None
    color: Color = None
    alpha: float | None = None
    ylabel: str | None = field(default="cumulative probability", kw_only=True)

    def __post_init__(self) -> None:
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        if self.nbins is not None and (
            not isinstance(self.nbins, Integral) or isinstance(self.nbins, bool) or self.nbins <= 0
        ):
            msg = f"nbins must be a positive integer or None, but received {self.nbins}"
            raise InvalidSpecError(msg)
        # Coerced with ``np.asarray`` so a spec can be constructed directly
        # (e.g. ``CdfSpec(values=[1, 2, 3])``) and not only through
        # ``plotmux.cdf``, which already converts its input before
        # construction. Mirrors ``HistogramSpec.__post_init__``.
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
