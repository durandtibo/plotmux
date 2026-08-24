r"""Render a ``HistogramSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any

import xy

from plotmux.core.range import find_range

if TYPE_CHECKING:
    from plotmux.core.specs import HistogramSpec


def render_histogram(spec: HistogramSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``HistogramSpec`` into an xy ``Chart``.

    Args:
        spec: The histogram spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.hist``.

    Returns:
        The resulting xy ``Chart``.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    return xy.histogram_chart(
        xy.hist(
            spec.values,
            bins=spec.bins,
            range=(xmin, xmax),
            density=spec.density,
            name=spec.label,
            **kwargs,
        )
    )
