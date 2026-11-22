r"""Contain utility functions to compute the step curve of an empirical
CDF."""

from __future__ import annotations

__all__ = ["cdf_steps"]

import numpy as np


def cdf_steps(
    values: np.ndarray,
    *,
    nbins: int | None = None,
    xmin: float | None = None,
    xmax: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    r"""Compute the ``(x, y)`` vertices of the step curve of an
    empirical CDF.

    The curve is ``P(X <= x)`` over **all** the values. ``xmin`` and
    ``xmax`` restrict the vertices that are returned, they do not
    renormalize the curve.

    Without ``nbins`` the CDF is exact: a vertical jump of ``1 / n`` at
    each of the ``n`` sorted values (the vertices are
    ``(v0, 0), (v0, 1/n), (v1, 1/n), (v1, 2/n), ..., (v_n, 1)``,
    ``2 n`` vertices). With ``nbins`` the values are binned first
    over their own range, and each bin is a jump followed by a flat
    run (``2 * nbins + 1`` vertices), to bound the size of the output
    for a large input.

    Args:
        values: The 1-dimensional array of finite values. Must not be
            empty.
        nbins: The number of bins, or ``None`` for the exact CDF.
        xmin: The lower bound of the curve to return, or ``None`` to
            start at the first vertex.
        xmax: The upper bound of the curve to return, or ``None`` to
            end at the last vertex.

    Returns:
        An ``(x, y)`` pair of arrays of the same length.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import cdf_steps
        >>> x, y = cdf_steps(np.array([3.0, 1.0, 2.0, 4.0]))
        >>> x
        array([1., 1., 2., 2., 3., 3., 4., 4.])
        >>> y
        array([0.  , 0.25, 0.25, 0.5 , 0.5 , 0.75, 0.75, 1.  ])

        ```
    """
    x, y = _exact_steps(values) if nbins is None else _binned_steps(values, nbins)
    return _restrict(x, y, xmin, xmax)


def _exact_steps(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    r"""Compute the vertices of the exact empirical CDF.

    Args:
        values: The 1-dimensional array of values. Must not be empty.

    Returns:
        The ``(x, y)`` vertices, ``2 * len(values)`` of each.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import _exact_steps
        >>> _exact_steps(np.array([2.0, 1.0]))
        (array([1., 1., 2., 2.]), array([0. , 0.5, 0.5, 1. ]))

        ```
    """
    sorted_values = np.sort(values).astype(float)
    n = sorted_values.size
    steps = np.arange(n + 1) / n
    x = np.repeat(sorted_values, 2)
    y = np.empty(2 * n)
    y[0::2] = steps[:-1]
    y[1::2] = steps[1:]
    return x, y


def _binned_steps(values: np.ndarray, nbins: int) -> tuple[np.ndarray, np.ndarray]:
    r"""Compute the vertices of the binned empirical CDF.

    Args:
        values: The 1-dimensional array of values. Must not be empty.
        nbins: The number of bins.

    Returns:
        The ``(x, y)`` vertices, ``2 * nbins + 1`` of each, from
            ``(min, 0)`` to ``(max, 1)``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import _binned_steps
        >>> x, y = _binned_steps(np.arange(5.0), nbins=2)
        >>> x
        array([0., 0., 2., 2., 4.])
        >>> y
        array([0. , 0.4, 0.4, 1. , 1. ])

        ```
    """
    counts, edges = np.histogram(values, bins=nbins)
    cumulative = np.cumsum(counts) / counts.sum()
    # A jump at the left edge of each bin up to the new cumulative height,
    # then a flat run to its right edge.
    x = np.empty(2 * nbins + 1)
    y = np.empty(2 * nbins + 1)
    x[0] = edges[0]
    y[0] = 0.0
    x[1::2] = edges[:-1]
    x[2::2] = edges[1:]
    y[1::2] = cumulative
    y[2::2] = cumulative
    return x, y


def _restrict(
    x: np.ndarray, y: np.ndarray, xmin: float | None, xmax: float | None
) -> tuple[np.ndarray, np.ndarray]:
    r"""Keep the vertices of a step curve inside ``[xmin, xmax]``.

    The curve is not renormalized: a vertex is added on each bound that
    cuts the curve, at the height of the step function there.

    Args:
        x: The x vertices, in increasing order.
        y: The y vertices.
        xmin: The lower bound, or ``None``.
        xmax: The upper bound, or ``None``.

    Returns:
        The restricted ``(x, y)`` pair.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import _restrict
        >>> x, y = _restrict(np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.5, 1.0]), 0.5, None)
        >>> x
        array([0.5, 1. , 2. ])
        >>> y
        array([0. , 0.5, 1. ])

        ```
    """
    if xmin is None and xmax is None:
        return x, y
    lo = x[0] if xmin is None else xmin
    hi = x[-1] if xmax is None else xmax
    keep = (x >= lo) & (x <= hi)
    kept_x, kept_y = x[keep], y[keep]
    if kept_x.size == 0 or kept_x[0] > lo:
        kept_x = np.concatenate(([lo], kept_x))
        kept_y = np.concatenate(([_height(x, y, lo)], kept_y))
    if kept_x[-1] < hi:
        kept_x = np.concatenate((kept_x, [hi]))
        kept_y = np.concatenate((kept_y, [_height(x, y, hi)]))
    return kept_x, kept_y


def _height(x: np.ndarray, y: np.ndarray, at: float) -> float:
    r"""Return the height of a step curve at ``at``.

    Args:
        x: The x vertices, in increasing order.
        y: The y vertices.
        at: The position.

    Returns:
        The ``y`` of the last vertex whose ``x`` is at most ``at``,
            ``0`` before the first vertex.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import _height
        >>> _height(np.array([0.0, 1.0, 1.0]), np.array([0.0, 0.0, 0.5]), 1.0)
        0.5

        ```
    """
    index = int(np.searchsorted(x, at, side="right")) - 1
    return float(y[index]) if index >= 0 else 0.0
