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
    # ``spec.color``/``spec.edgecolor``, once set, are already canonical
    # RGBA tuples: they went through ``parse_color`` in
    # ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    if spec.edgecolor is not None:
        # ``xy.scatter``'s ``stroke``/``stroke_width`` draw a separate
        # marker edge on top of ``color``'s fill (``stroke_width`` defaults
        # to ``0.0``, no visible edge, so a nonzero width is needed for
        # ``stroke`` to actually show).
        kwargs.setdefault(
            "stroke", rgba_to_xy(cast("tuple[float, float, float, float]", spec.edgecolor))
        )
        kwargs.setdefault("stroke_width", 1.0)
    # ``xy.scatter``'s ``symbol`` accepts plotmux's portable shape names
    # directly (``"circle"``/``"square"``/``"triangle"``/``"diamond"``/
    # ``"cross"``/``"x"``), unlike matplotlib, so no translation table is
    # needed here (see ``plotmux.backends.matplotlib.scatter.MARKER_STYLE``).
    if spec.marker is not None:
        kwargs.setdefault("symbol", spec.marker)
    return xy.scatter_chart(
        xy.scatter(spec.x, spec.y, name=spec.label, color=color, **kwargs),
    )
