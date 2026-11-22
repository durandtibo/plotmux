r"""Contain utility functions to build the arrays held by the specs."""

from __future__ import annotations

__all__ = ["to_paired_arrays", "to_readonly_array"]

from typing import TYPE_CHECKING

import numpy as np

from plotmux.exceptions import InvalidSpecError

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


def to_paired_arrays(x: ArrayLike, y: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    r"""Convert ``x`` and ``y`` to read-only arrays and check that they
    have the same length.

    Shared by every mark that pairs an ``x`` array with a ``y`` array
    (``LineSpec``, ``ScatterSpec``, ``BarSpec``), so the check and its
    error message are written once.

    Args:
        x: The array of x values.
        y: The array of y values.

    Returns:
        The ``(x, y)`` pair, each converted by ``to_readonly_array``.

    Raises:
        InvalidSpecError: if ``x`` or ``y`` is not 1-dimensional, or
            if they do not have the same length. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> from plotmux.utils.array import to_paired_arrays
        >>> x, y = to_paired_arrays([1, 2, 3], [4, 5, 6])
        >>> x
        array([1, 2, 3])

        ```
    """
    x = to_readonly_array(x)
    y = to_readonly_array(y)
    if x.ndim != 1 or y.ndim != 1:
        msg = f"x and y must be 1-dimensional, but received shapes {x.shape} and {y.shape}"
        raise InvalidSpecError(msg)
    if x.shape[0] != y.shape[0]:
        msg = f"x and y must have the same length, but received {x.shape[0]} and {y.shape[0]}"
        raise InvalidSpecError(msg)
    return x, y
