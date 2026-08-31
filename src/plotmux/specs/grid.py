r"""Contain the backend-agnostic grid-layout specification."""

from __future__ import annotations

__all__ = ["GridSpec"]

from dataclasses import dataclass
from numbers import Integral

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec


@dataclass(frozen=True)
class GridSpec(BaseSpec):
    r"""Define a spec that lays out multiple child specs as independent
    panels in a grid.

    Unlike ``LayerSpec`` (multiple specs drawn onto *one* shared axes,
    see ``plotmux.specs.LayerSpec``), each child here gets its own,
    independent panel -- the backend-agnostic equivalent of
    matplotlib's ``pyplot.subplots``. A child may itself be a
    ``LayerSpec`` (several series sharing one panel's axes); a nested
    ``GridSpec`` is rejected for the same reason ``LayerSpec`` rejects
    nesting: layout is one flat pass over ``cells``, so callers must
    flatten nested grids themselves.

    Args:
        cells: The child specs to draw, one independent panel per
            spec, in row-major order (left to right, top to bottom).
            Must be non-empty.
        ncols: The number of columns in the grid. Rows are filled
            left to right; the last row is left short (its remaining
            panels left empty) when ``len(cells)`` is not a multiple
            of ``ncols``. Must be a positive integer.
        title: An optional figure-level title, shown once above the
            whole grid (not any individual cell). Inherited from
            ``BaseSpec``.

    ``xlabel``/``ylabel``/``xscale``/``yscale``, also inherited from
    ``BaseSpec``, have no meaning at the grid level -- each cell keeps
    its own -- so every backend's grid renderer ignores them.

    Raises:
        ValueError: if ``cells`` is empty, contains a ``GridSpec``,
            or ``ncols`` is not a positive integer.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import GridSpec, HistogramSpec, LineSpec
        >>> spec = GridSpec(
        ...     cells=(
        ...         HistogramSpec(values=np.arange(101), bins=10),
        ...         LineSpec(x=np.arange(10), y=np.arange(10)),
        ...     ),
        ...     ncols=2,
        ... )
        >>> len(spec.cells)
        2

        ```
    """

    cells: tuple[BaseSpec, ...]
    ncols: int = 1

    def __post_init__(self) -> None:
        if not self.cells:
            msg = "cells must contain at least one spec"
            raise InvalidSpecError(msg)
        if any(isinstance(child, GridSpec) for child in self.cells):
            msg = "cells must not contain a GridSpec (nesting is not supported)"
            raise InvalidSpecError(msg)
        if not isinstance(self.ncols, Integral) or isinstance(self.ncols, bool) or self.ncols <= 0:
            msg = f"ncols must be a positive integer, but received {self.ncols}"
            raise InvalidSpecError(msg)
