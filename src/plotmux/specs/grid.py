r"""Contain the backend-agnostic grid-layout specification."""

from __future__ import annotations

__all__ = ["FigureSpec", "GridSpec"]

from dataclasses import dataclass
from numbers import Integral
from typing import TypeAlias

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import Spec
from plotmux.specs.panel import PanelSpec


@dataclass(frozen=True, eq=False)
class GridSpec(Spec):
    r"""Define a grid of independent panels.

    Each panel is its own axes with its own marks and style, the
    backend-agnostic equivalent of matplotlib's ``pyplot.subplots``.
    A grid holds panels, and a panel holds marks, so neither a grid in
    a grid nor a panel in a panel can be built.

    Args:
        panels: The panels to draw, in row-major order (left to right,
            top to bottom). Must be non-empty.
        ncols: The number of columns in the grid. The last row is left
            short when ``len(panels)`` is not a multiple of ``ncols``.
            Must be a positive integer.
        title: An optional title shown once above the whole grid.

    Raises:
        InvalidSpecError: if ``panels`` is empty or holds an object
            that is not a ``PanelSpec``, or ``ncols`` is not a
            positive integer. Also a ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import GridSpec, HistogramSpec, LineSpec, PanelSpec
        >>> spec = GridSpec(
        ...     panels=(
        ...         PanelSpec(marks=(HistogramSpec(values=np.arange(101), bins=10),)),
        ...         PanelSpec(marks=(LineSpec(x=np.arange(10), y=np.arange(10)),)),
        ...     ),
        ...     ncols=2,
        ... )
        >>> len(spec.panels)
        2

        ```
    """

    panels: tuple[PanelSpec, ...]
    ncols: int = 1
    title: str | None = None

    def __post_init__(self) -> None:
        panels = tuple(self.panels)
        if not panels:
            msg = "panels must contain at least one panel"
            raise InvalidSpecError(msg)
        for panel in panels:
            if not isinstance(panel, PanelSpec):
                msg = f"panels must hold PanelSpec objects, but received {type(panel).__name__}"
                raise InvalidSpecError(msg)
        object.__setattr__(self, "panels", panels)
        if not isinstance(self.ncols, Integral) or isinstance(self.ncols, bool) or self.ncols <= 0:
            msg = f"ncols must be a positive integer, but received {self.ncols}"
            raise InvalidSpecError(msg)


#: The spec of a figure: one panel, or a grid of panels.
FigureSpec: TypeAlias = PanelSpec | GridSpec
