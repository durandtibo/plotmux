r"""Render a ``SlopeSpec`` into an xy ``Chart``, given the x-range it
should span.
"""

from __future__ import annotations

__all__ = ["render_slope"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy

if TYPE_CHECKING:
    from plotmux.specs import SlopeSpec


def render_slope(spec: SlopeSpec, xrange: tuple[float, float], **kwargs: Any) -> xy.Chart:
    r"""Render a ``SlopeSpec`` into an xy ``Chart``.

    Unlike matplotlib's ``Axes.axline``/bokeh's ``bokeh.models.Slope``
    (see ``plotmux.backends.matplotlib.slope``/
    ``plotmux.backends.bokeh.slope``), xy has no native "line by
    slope, independent of data range" primitive: ``xy.line`` needs
    concrete data points. So this draws a plain two-point line between
    ``(xrange[0], gradient * xrange[0] + intercept)`` and
    ``(xrange[1], gradient * xrange[1] + intercept)`` -- ``xrange`` is
    supplied by the caller (``plotmux.backends.xy.layer.render_layer``,
    via ``plotmux.utils.slope.resolve_slope_xrange``), computed from
    the ``SlopeSpec``'s sibling children in the same ``LayerSpec``,
    since a standalone ``SlopeSpec`` has no data of its own to derive
    a range from (see DESIGN.md, section 8.1) -- this renderer is
    registered only in ``render_layer``'s own dispatch table, not in
    ``XyBackend._RENDERERS``.

    Args:
        spec: The slope spec to render.
        xrange: The ``(min, max)`` x-range the line should span,
            computed from ``spec``'s siblings.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.line``.

    Returns:
        The resulting xy ``Chart``.
    """
    x0, x1 = xrange
    y0 = spec.gradient * x0 + spec.intercept
    y1 = spec.gradient * x1 + spec.intercept
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``SlopeSpec.__post_init__``.
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
        xy.line([x0, x1], [y0, y1], name=spec.label, color=color, **kwargs),
    )
