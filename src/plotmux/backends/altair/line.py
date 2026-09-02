r"""Render a ``LineSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_line"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import STROKE_DASH, prepare_color, rgba_to_altair

if TYPE_CHECKING:
    from plotmux.specs import LineSpec


def render_line(spec: LineSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``LineSpec`` into an altair ``Chart``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    Args:
        spec: The line spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_line``.

    Returns:
        The resulting altair ``Chart``.
    """
    data = [{"x": x, "y": y} for x, y in zip(spec.x, spec.y)]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``LineSpec.__post_init__``.
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
