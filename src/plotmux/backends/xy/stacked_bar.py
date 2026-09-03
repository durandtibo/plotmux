r"""Render a ``StackedBarSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_stacked_bar"]

from typing import TYPE_CHECKING, Any, cast

import numpy as np
import xy

from plotmux.backends.xy.style import rgba_to_xy

if TYPE_CHECKING:
    from plotmux.specs import StackedBarSpec


def render_stacked_bar(spec: StackedBarSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``StackedBarSpec`` into an xy ``Chart``.

    xy's own ``xy.bar`` has a native ``mode="stacked"`` layout over a
    matrix-valued ``y`` (one column per series, ``series=`` naming
    each), so this needs no manual running-total offset the way
    matplotlib's/plotly's own renderers do -- much like bokeh's
    ``vbar_stack``.

    Args:
        spec: The stacked-bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.bar``.

    Returns:
        The resulting xy ``Chart``.
    """
    y = np.stack([s.y for s in spec.series], axis=1)
    labels = [s.label if s.label is not None else f"series_{i}" for i, s in enumerate(spec.series)]
    # Every series' ``color``, once set, is already a canonical RGBA tuple:
    # it went through ``parse_color`` in ``StackedBarSpec.__post_init__``.
    colors = [rgba_to_xy(cast("tuple[float, float, float, float]", s.color)) for s in spec.series]
    kwargs.setdefault("width", spec.width)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    return xy.bar_chart(
        xy.bar(spec.x, y, mode="stacked", series=labels, colors=colors, **kwargs),
    )
