r"""Render a ``BarSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_bar"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import prepare_color, rgba_to_altair
from plotmux.utils.categorical import is_categorical

if TYPE_CHECKING:
    from plotmux.specs import BarSpec


def render_bar(spec: BarSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``BarSpec`` into an altair ``Chart``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    ``spec.width`` (a bar width in ``x`` data units, like
    matplotlib's/bokeh's own ``width``) has no direct altair
    equivalent: Vega-Lite derives a bar mark's rendered width from its
    band/continuous scale rather than accepting a data-unit width at
    construction time, so it is deliberately not forwarded here.

    Args:
        spec: The bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_bar``.

    Returns:
        The resulting altair ``Chart``.
    """
    data = [{"x": x, "y": y} for x, y in zip(spec.x, spec.y)]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``BarSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    # ``x`` is encoded ``:N`` (nominal) for a categorical (string) x-axis
    # and ``:Q`` (quantitative) otherwise -- unlike ``:Q``, which Vega-Lite
    # expects numbers under, a hardcoded ``:Q`` would produce invalid
    # encoded data for a string ``spec.x`` (this is also why the shared
    # ``apply_common_style`` re-``encode``s ``x``/``y`` with a fixed
    # ``:Q``-implying ``alt.Scale`` -- see its docstring -- but does not
    # touch the field-name/type specifier itself, so this stays in effect).
    x_type = "N" if is_categorical(spec.x) else "Q"
    chart = alt.Chart(alt.Data(values=data)).mark_bar(**kwargs).encode(x=f"x:{x_type}", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
