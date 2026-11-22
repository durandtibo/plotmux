r"""Contain the backend-agnostic histogram specification."""

from __future__ import annotations

__all__ = ["HistogramSpec"]

from dataclasses import dataclass, field
from numbers import Integral
from typing import TYPE_CHECKING

import numpy as np

from plotmux.colors import parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Bars
from plotmux.specs.base import MarkSpec
from plotmux.utils.array import to_readonly_array
from plotmux.utils.finite import drop_non_finite
from plotmux.utils.range import check_range_bounds, find_range

if TYPE_CHECKING:
    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class HistogramSpec(MarkSpec):
    r"""Define a backend-agnostic histogram mark.

    Args:
        values: The array of values to plot.
        bins: The number of histogram bins. Must be a positive
            integer.
        xmin: Specifies the lower bound of the range of the values
            that are binned. It can be an explicit value, a quantile
            string such as ``"q0.1"``, or ``None`` to use the minimum
            of ``values``. See ``plotmux.utils.range.find_range`` for
            the exact semantics. It is not an axis limit (see
            ``PanelSpec.xmin``): the axes autoscale on the bars.
        xmax: Specifies the upper bound of the range of the values
            that are binned. Same semantics as ``xmin`` but for the
            upper bound.
        density: If ``True``, each bin displays the bin's raw count
            divided by the total number of counts and the bin width,
            so that the area under the histogram integrates to 1.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``. ``NaN`` and ``inf`` values of ``values`` are
    dropped, and a ``UserWarning`` with their count is emitted once,
    when the spec is built. The quantile bounds are computed on the
    finite values.

    Raises:
        InvalidSpecError: if ``bins`` is not a positive integer,
            ``values`` is not 1-dimensional, is empty, is not numeric
            or has no finite value, or ``xmin`` and ``xmax`` are both
            explicit numeric values with ``xmin >= xmax``. Also a
            ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

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
    xmin: float | str | None = field(default=None, kw_only=True)
    xmax: float | str | None = field(default=None, kw_only=True)
    density: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.bins, Integral) or isinstance(self.bins, bool) or self.bins <= 0:
            msg = f"bins must be a positive integer, but received {self.bins}"
            raise InvalidSpecError(msg)
        values = to_readonly_array(self.values)
        if values.ndim != 1:
            msg = f"values must be 1-dimensional, but received shape {values.shape}"
            raise InvalidSpecError(msg)
        if values.size == 0:
            msg = "values must not be empty"
            raise InvalidSpecError(msg)
        values = drop_non_finite(values, owner="HistogramSpec")
        values.flags.writeable = False
        object.__setattr__(self, "values", values)
        check_range_bounds(self.xmin, self.xmax)

    def x_extent(self) -> tuple[float, float] | None:
        return find_range(self.values, self.xmin, self.xmax)

    def is_categorical(self) -> bool | None:
        return False

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        del extent  # the mark has data of its own
        counts, edges = np.histogram(
            self.values,
            bins=self.bins,
            range=find_range(self.values, self.xmin, self.xmax),
            density=self.density,
        )
        return (
            Bars(
                x=(edges[:-1] + edges[1:]) / 2,
                height=counts.astype(float),
                base=np.zeros(counts.shape),
                width=np.diff(edges),
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                label=self.label,
            ),
        )
