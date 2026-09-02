r"""Render a ``LineSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_line"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy

if TYPE_CHECKING:
    from plotmux.specs import LineSpec


def render_line(spec: LineSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``LineSpec`` into an xy ``Chart``.

    Args:
        spec: The line spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.line``.

    Returns:
        The resulting xy ``Chart``.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``LineSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    if spec.linewidth is not None:
        kwargs.setdefault("width", spec.linewidth)
    if spec.linestyle != "solid":
        kwargs.setdefault("dash", spec.linestyle)
    return xy.line_chart(
        xy.line(spec.x, spec.y, name=spec.label, color=color, **kwargs),
    )
