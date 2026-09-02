r"""Render a ``BarSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_bar"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy

if TYPE_CHECKING:
    from plotmux.specs import BarSpec


def render_bar(spec: BarSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``BarSpec`` into an xy ``Chart``.

    Args:
        spec: The bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.bar``.

    Returns:
        The resulting xy ``Chart``.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``BarSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    kwargs.setdefault("width", spec.width)
    return xy.bar_chart(
        xy.bar(spec.x, spec.y, name=spec.label, color=color, **kwargs),
    )
