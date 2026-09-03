r"""Render a ``StackedBarSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_stacked_bar"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import rgba_to_altair
from plotmux.utils.categorical import is_categorical

if TYPE_CHECKING:
    from plotmux.specs import StackedBarSpec


def render_stacked_bar(spec: StackedBarSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``StackedBarSpec`` into an altair ``Chart``.

    Reshapes ``spec`` into long-form data (one row per ``(x, series)``
    pair, see DESIGN.md, section 8.4) and lets Vega-Lite stack the bar
    mark automatically: it stacks whenever ``y`` is quantitative and
    ``color`` is a discrete encoding, no explicit stacking argument
    needed, unlike matplotlib's/plotly's own renderers, which build
    the stack themselves.

    ``order="series:O"`` pins the stacking order to ``spec.series``'
    own order (bottom to top); without it Vega-Lite would stack in an
    unspecified order for a nominal ``color`` field.

    Args:
        spec: The stacked-bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_bar``.

    Returns:
        The resulting altair ``Chart``.
    """
    labels = [s.label if s.label is not None else f"series_{i}" for i, s in enumerate(spec.series)]
    # Every series' ``color``, once set, is already a canonical RGBA tuple:
    # it went through ``parse_color`` in ``StackedBarSpec.__post_init__``.
    colors = [
        rgba_to_altair(cast("tuple[float, float, float, float]", s.color)) for s in spec.series
    ]
    data = [
        {"x": x, "y": y, "series": label, "order": i}
        for i, (label, series) in enumerate(zip(labels, spec.series))
        for x, y in zip(spec.x, series.y)
    ]
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    x_type = "N" if is_categorical(spec.x) else "Q"
    legend = alt.Legend() if any(s.label is not None for s in spec.series) else None
    return (
        alt.Chart(alt.Data(values=data))
        .mark_bar(**kwargs)
        .encode(
            x=f"x:{x_type}",
            y="y:Q",
            order="order:O",
            color=alt.Color(
                "series:N", scale=alt.Scale(domain=labels, range=colors), legend=legend
            ),
        )
    )
