r"""Render a ``SlopeSpec`` into an altair ``Chart``, given the x-range
it should span."""

from __future__ import annotations

__all__ = ["render_slope"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import STROKE_DASH, prepare_color, rgba_to_altair

if TYPE_CHECKING:
    from plotmux.specs import SlopeSpec


def render_slope(spec: SlopeSpec, xrange: tuple[float, float], **kwargs: Any) -> alt.Chart:
    r"""Render a ``SlopeSpec`` into an altair ``Chart``.

    Unlike matplotlib's ``Axes.axline``/bokeh's ``bokeh.models.Slope``
    (see ``plotmux.backends.matplotlib.slope``/
    ``plotmux.backends.bokeh.slope``), altair has no native "line by
    slope, independent of data range" primitive: a ``mark_line`` needs
    concrete data points. So this draws a plain two-point line between
    ``(xrange[0], gradient * xrange[0] + intercept)`` and
    ``(xrange[1], gradient * xrange[1] + intercept)`` -- ``xrange`` is
    supplied by the caller (``plotmux.backends.altair.layer.render_layer``,
    via ``plotmux.utils.slope.resolve_slope_xrange``), computed from the
    ``SlopeSpec``'s sibling children in the same ``LayerSpec``, since a
    standalone ``SlopeSpec`` has no data of its own to derive a range
    from (see DESIGN.md, section 8.1) -- this renderer is registered
    only in ``render_layer``'s own dispatch table, not in
    ``AltairBackend._RENDERERS``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    Args:
        spec: The slope spec to render.
        xrange: The ``(min, max)`` x-range the line should span,
            computed from ``spec``'s siblings.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_line``.

    Returns:
        The resulting altair ``Chart``.
    """
    x0, x1 = xrange
    data = [
        {"x": x0, "y": spec.gradient * x0 + spec.intercept},
        {"x": x1, "y": spec.gradient * x1 + spec.intercept},
    ]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``SlopeSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    if spec.linewidth is not None:
        kwargs.setdefault("strokeWidth", spec.linewidth)
    if spec.linestyle in STROKE_DASH:
        kwargs.setdefault("strokeDash", STROKE_DASH[spec.linestyle])
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    chart = alt.Chart(alt.Data(values=data)).mark_line(**kwargs).encode(x="x:Q", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
