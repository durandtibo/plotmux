r"""Contain utility functions to build the arrays held by the specs."""

from __future__ import annotations

__all__ = ["to_readonly_array"]

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


def to_readonly_array(values: ArrayLike) -> np.ndarray:
    r"""Convert the input to a read-only array that owns its data.

    The data is always copied, so the result never shares memory with
    the input: changing the input afterwards does not change the
    result, and the result cannot be changed in place.

    Args:
        values: The values to convert.

    Returns:
        A new read-only ``numpy.ndarray``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils import to_readonly_array
        >>> a = np.arange(3)
        >>> b = to_readonly_array(a)
        >>> a[0] = 99
        >>> b
        array([0, 1, 2])
        >>> b.flags.writeable
        False

        ```
    """
    array = np.array(values, copy=True)
    array.flags.writeable = False
    return array
