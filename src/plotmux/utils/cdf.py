r"""Contain utility functions to compute an empirical CDF's step
coordinates."""

from __future__ import annotations

__all__ = ["compute_cdf_steps"]

import numpy as np


def compute_cdf_steps(
    values: np.ndarray, bins: int, xmin: float, xmax: float
) -> tuple[np.ndarray, np.ndarray]:
    r"""Compute the ``(x, y)`` vertices of a binned empirical CDF's
    step curve.

    Bin counts are computed with ``numpy.histogram`` over
    ``(xmin, xmax)`` and turned into a cumulative, density-normalized
    curve, the same approach matplotlib's own
    ``Axes.hist(..., density=True, cumulative=True,
    histtype="step")`` takes internally (see
    ``plotmux.backends.matplotlib.cdf.render_cdf``, which uses that
    call directly instead of this helper). bokeh/altair/xy have no
    equivalent single-call cumulative-step histogram, so this returns
    explicit polyline vertices -- two points per bin edge (a vertical
    jump to the new cumulative height, then a horizontal run across
    the bin) -- that any of those backends' plain line/step mark can
    draw as-is.

    Args:
        values: The array of values to compute the CDF from.
        bins: The number of bins to use.
        xmin: The lower bound of the x-axis range.
        xmax: The upper bound of the x-axis range.

    Returns:
        An ``(x, y)`` pair of arrays, each of length ``2 * bins + 1``,
            tracing the step curve from ``(xmin, 0)`` up to
            ``(xmax, 1)``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.cdf import compute_cdf_steps
        >>> x, y = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
        >>> x.shape, y.shape
        ((21,), (21,))

        ```
    """
    counts, edges = np.histogram(values, bins=bins, range=(xmin, xmax))
    cumulative = np.cumsum(counts) / counts.sum()
    # Vertices: start at (edges[0], 0), then for each bin a vertical jump
    # at its left edge up to the new cumulative height, followed by a
    # horizontal run to its right edge at that same height -- see the
    # docstring above for why this explicit shape is built rather than
    # relying on a backend-specific step-interpolation mode.
    x = np.empty(2 * bins + 1)
    y = np.empty(2 * bins + 1)
    x[0] = edges[0]
    y[0] = 0.0
    x[1::2] = edges[:-1]
    x[2::2] = edges[1:]
    y[1::2] = cumulative
    y[2::2] = cumulative
    return x, y
