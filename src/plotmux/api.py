r"""Contain the public plotting API."""

from __future__ import annotations

__all__ = ["hist"]

from typing import TYPE_CHECKING, Any

import numpy as np

from plotmux.backends.registry import get_backend
from plotmux.config import get_default_backend
from plotmux.core.specs import HistogramSpec
from plotmux.figure import Figure

if TYPE_CHECKING:
    from collections.abc import Sequence


def hist(
    values: Sequence[float] | np.ndarray,
    *,
    bins: int = 30,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    label: str | None = None,
    density: bool = False,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a histogram.

    Args:
        values: The array of values to plot.
        bins: The number of histogram bins. Must be a positive
            integer.
        xmin: Specifies the lower bound of the x-axis range. It can
            be an explicit value, a quantile string such as
            ``"q0.1"``, or ``None`` to use the minimum of ``values``.
        xmax: Specifies the upper bound of the x-axis range. Same
            semantics as ``xmin`` but for the upper bound.
        label: An optional label used e.g. in the legend.
        density: If ``True``, draw and return a probability
            density: each bin will display the bin's raw count
            divided by the total number of counts and the bin
            width, so that the area under the histogram integrates
            to 1. Defaults to ``False``.
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=3)  # doctest: +SKIP

        ```
    """
    spec = HistogramSpec(
        values=np.asarray(values),
        bins=bins,
        xmin=xmin,
        xmax=xmax,
        label=label,
        density=density,
    )
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)
