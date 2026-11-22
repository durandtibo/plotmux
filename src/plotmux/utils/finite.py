r"""Contain the input policy of the non-finite values (``NaN`` and ``inf``).

The policy depends on the chart:

- A histogram or a CDF drops ``NaN`` and ``inf`` (``drop_non_finite``).
- A line or a scatter plot keeps ``NaN`` (a gap in the line, no point)
  and rejects ``inf`` (``check_no_inf``).
"""

from __future__ import annotations

__all__ = ["check_no_inf", "drop_non_finite"]

import warnings
from typing import TYPE_CHECKING

import numpy as np

from plotmux.exceptions import InvalidSpecError

if TYPE_CHECKING:
    from numpy.typing import NDArray


def drop_non_finite(values: NDArray, *, owner: str, name: str = "values") -> NDArray:
    r"""Drop the ``NaN`` and ``inf`` of a 1-dimensional array.

    A ``UserWarning`` with the number of dropped values is emitted
    when at least one value is dropped. The warning is emitted by the
    function that calls it once, at the construction of the spec, so
    it is not repeated at each render.

    Args:
        values: The 1-dimensional array to filter.
        owner: The name of the spec, used in the messages.
        name: The name of the array, used in the messages.

    Returns:
        The finite values, in the same order. The input array itself
            (not a copy) if every value is finite.

    Raises:
        InvalidSpecError: if ``values`` is not numeric, or has no
            finite value. Also a ``ValueError``.

    Example:
        ```pycon
        >>> import warnings
        >>> import numpy as np
        >>> from plotmux.utils.finite import drop_non_finite
        >>> with warnings.catch_warnings():
        ...     warnings.simplefilter("ignore")
        ...     drop_non_finite(np.array([1.0, np.nan, 3.0, np.inf]), owner="HistogramSpec")
        ...
        array([1., 3.])

        ```
    """
    if values.dtype.kind not in "biuf":
        msg = f"{owner}: {name} must be numeric, but received dtype {values.dtype}"
        raise InvalidSpecError(msg)
    finite = np.isfinite(values)
    num_dropped = int(finite.size - np.count_nonzero(finite))
    if num_dropped == 0:
        return values
    if num_dropped == values.size:
        msg = f"{owner}: {name} must contain at least one finite value, but all {num_dropped} are NaN or inf"
        raise InvalidSpecError(msg)
    msg = (
        f"{owner}: {num_dropped} non-finite value(s) (NaN or inf) detected in {name} "
        f"and filtered out"
    )
    # The caller is ``__post_init__``, called by the generated ``__init__``,
    # called by the user's code.
    warnings.warn(msg, UserWarning, stacklevel=4)
    return values[finite]


def check_no_inf(values: NDArray, *, owner: str, name: str) -> None:
    r"""Check that an array has no ``inf`` or ``-inf``.

    ``NaN`` is accepted, and so are the non-numeric arrays (e.g. the
    categories of a bar chart).

    Args:
        values: The array to check.
        owner: The name of the spec, used in the message.
        name: The name of the array, used in the message.

    Raises:
        InvalidSpecError: if ``values`` has an infinite value. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.finite import check_no_inf
        >>> check_no_inf(np.array([1.0, np.nan]), owner="LineSpec", name="y")

        ```
    """
    if values.dtype.kind in "fc" and np.isinf(values).any():
        num_inf = int(np.isinf(values).sum())
        msg = f"{owner}: {name} must not contain inf, but received {num_inf} infinite value(s)"
        raise InvalidSpecError(msg)
