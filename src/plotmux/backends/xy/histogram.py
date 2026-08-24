r"""Render a ``HistogramSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy
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
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``HistogramSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    return xy.histogram_chart(
        xy.hist(
            spec.values,
            bins=spec.bins,
            range=(xmin, xmax),
            density=spec.density,
            name=spec.label,
            color=color,
            **kwargs,
        )
    )
