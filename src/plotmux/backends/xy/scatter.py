r"""Render a ``ScatterSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy

if TYPE_CHECKING:
    from plotmux.specs import ScatterSpec


def render_scatter(spec: ScatterSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``ScatterSpec`` into an xy ``Chart``.

    Args:
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.scatter``.

    Returns:
        The resulting xy ``Chart``.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    return xy.scatter_chart(
        xy.scatter(spec.x, spec.y, name=spec.label, color=color, **kwargs),
    )
