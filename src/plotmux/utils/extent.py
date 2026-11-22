r"""Contain a small helper to compute the extent of an array."""

from __future__ import annotations

__all__ = ["finite_extent"]

import numpy as np


def finite_extent(values: np.ndarray, *, pad: float = 0.0) -> tuple[float, float] | None:
    r"""Compute the ``(min, max)`` of the numeric values of an array.

    ``NaN`` values are ignored.

    Args:
        values: The array to measure.
        pad: A margin subtracted from the minimum and added to the
            maximum (e.g. half the width of a bar).

    Returns:
        The ``(min - pad, max + pad)`` pair, or ``None`` if the array
            is not numeric, is empty, or has only ``NaN``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.extent import finite_extent
        >>> finite_extent(np.array([1.0, np.nan, 3.0]))
        (1.0, 3.0)
        >>> finite_extent(np.array([1.0, 3.0]), pad=0.5)
        (0.5, 3.5)
        >>> finite_extent(np.array(["a", "b"])) is None
        True

        ```
    """
    if values.dtype.kind not in "biuf" or values.size == 0 or np.isnan(values).all():
        return None
    return float(np.nanmin(values)) - pad, float(np.nanmax(values)) + pad
