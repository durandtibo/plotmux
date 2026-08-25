r"""Render a ``ScatterSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import prepare_color, rgba_to_altair

if TYPE_CHECKING:
    from plotmux.specs import ScatterSpec


def render_scatter(spec: ScatterSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``ScatterSpec`` into an altair ``Chart``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    Args:
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_point``.

    Returns:
        The resulting altair ``Chart``.
    """
    data = [{"x": x, "y": y} for x, y in zip(spec.x, spec.y)]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    chart = alt.Chart(alt.Data(values=data)).mark_point(**kwargs).encode(x="x:Q", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
