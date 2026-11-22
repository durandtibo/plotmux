r"""Contain the backend-agnostic empirical CDF specification."""

from __future__ import annotations

__all__ = ["CdfSpec"]

from dataclasses import dataclass, field
from numbers import Integral
from typing import TYPE_CHECKING

from plotmux.colors import parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Line
from plotmux.specs.base import MarkSpec
from plotmux.utils.array import to_readonly_array
from plotmux.utils.cdf import cdf_steps
from plotmux.utils.finite import drop_non_finite
from plotmux.utils.range import check_range_bounds, find_range

if TYPE_CHECKING:
    import numpy as np

    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class CdfSpec(MarkSpec):
    r"""Define a backend-agnostic empirical cumulative distribution
    function (CDF) mark.

    The curve is the exact empirical ``P(X <= x)`` over all the
    values: a step of ``1 / n`` at each value. ``xmin`` and ``xmax``
    restrict what is drawn, they do not renormalize the curve.

    Args:
        values: The array of values to plot.
        nbins: ``None`` for the exact CDF (``2 n`` vertices), or a
            positive integer to bin the values first and bound the
            number of vertices (``2 * nbins + 1``) for a large input.
        xmin: Specifies the lower bound of the part of the curve that
            is drawn. It can be an explicit value, a quantile string
            such as ``"q0.1"``, or ``None`` to use the minimum of
            ``values``. See ``plotmux.utils.range.find_range`` for the
            exact semantics. It is not an axis limit (see
            ``PanelSpec.xmin``).
        xmax: Specifies the upper bound of the part of the curve that
            is drawn. Same semantics as ``xmin`` but for the upper
            bound.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``. ``NaN`` and ``inf`` values of ``values`` are
    dropped, and a ``UserWarning`` with their count is emitted once,
    when the spec is built. The quantile bounds are computed on the
    finite values.

    Raises:
        InvalidSpecError: if ``nbins`` is set and is not a positive
            integer, ``values`` is not 1-dimensional, is empty, is not
            numeric or has no finite value, or ``xmin`` and ``xmax`` are
            both explicit numeric values with ``xmin >= xmax``. Also a
            ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

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
    xmin: float | str | None = field(default=None, kw_only=True)
    xmax: float | str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.nbins is not None and (
            not isinstance(self.nbins, Integral) or isinstance(self.nbins, bool) or self.nbins <= 0
        ):
            msg = f"nbins must be a positive integer or None, but received {self.nbins}"
            raise InvalidSpecError(msg)
        values = to_readonly_array(self.values)
        if values.ndim != 1:
            msg = f"values must be 1-dimensional, but received shape {values.shape}"
            raise InvalidSpecError(msg)
        if values.size == 0:
            msg = "values must not be empty"
            raise InvalidSpecError(msg)
        values = drop_non_finite(values, owner="CdfSpec")
        values.flags.writeable = False
        object.__setattr__(self, "values", values)
        check_range_bounds(self.xmin, self.xmax)

    def x_extent(self) -> tuple[float, float] | None:
        return find_range(self.values, self.xmin, self.xmax)

    def is_categorical(self) -> bool | None:
        return False

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        lo, hi = find_range(self.values, self.xmin, self.xmax)
        x, y = cdf_steps(self.values, nbins=self.nbins, xmin=lo, xmax=hi)
        return (
            Line(
                x=x,
                y=y,
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                label=self.label,
            ),
        )
