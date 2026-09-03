r"""Render a ``StackedBarSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_stacked_bar", "stacked_bar_figure_kwargs"]

from typing import TYPE_CHECKING, Any, cast

from bokeh.models import ColumnDataSource

from plotmux.backends.bokeh.style import ALPHA, apply_fields, rgba_to_bokeh
from plotmux.utils.categorical import is_categorical

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import StackedBarSpec
    from plotmux.specs.base import BaseSpec


def stacked_bar_figure_kwargs(spec: BaseSpec) -> dict[str, Any]:
    r"""Return the extra ``figure()`` constructor kwargs a
    ``StackedBarSpec`` needs for a categorical x-axis.

    Same rationale as ``plotmux.backends.bokeh.bar.bar_figure_kwargs``,
    which this mirrors: a categorical ``spec.x`` needs a ``FactorRange``
    x-range set at ``figure()`` construction time, before
    ``render_stacked_bar`` draws any glyph.

    Args:
        spec: The stacked-bar spec to inspect. Not typed as
            ``StackedBarSpec`` directly since
            ``plotmux.backends.bokeh.backend._make_renderer``'s
            ``figure_kwargs`` hook is typed generically over
            ``BaseSpec``.

    Returns:
        ``{"x_range": list(spec.x)}`` when ``spec.x`` is categorical,
            an empty dict otherwise.
    """
    x = cast("StackedBarSpec", spec).x
    if is_categorical(x):
        return {"x_range": list(x)}
    return {}


def render_stacked_bar(fig: figure, spec: StackedBarSpec, **kwargs: Any) -> figure:
    r"""Render a ``StackedBarSpec`` onto a bokeh ``figure``.

    Uses bokeh's own ``figure.vbar_stack`` primitive directly, bokeh's
    native stacking mechanism, matched almost one-to-one -- unlike
    matplotlib's/plotly's own renderers, which have to build the stack
    themselves (a running ``bottom=``/``base=`` offset).

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The stacked-bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.vbar_stack``.

    Returns:
        The ``figure`` the bars were drawn onto.
    """
    stackers = [f"series_{i}" for i in range(len(spec.series))]
    data: dict[str, Any] = {"x": spec.x, **{k: s.y for k, s in zip(stackers, spec.series)}}
    source = ColumnDataSource(data=data)
    # Every series' ``color``, once set, is already a canonical RGBA tuple:
    # it went through ``parse_color`` in ``StackedBarSpec.__post_init__``.
    colors = [
        rgba_to_bokeh(cast("tuple[float, float, float, float]", s.color)) for s in spec.series
    ]
    style: dict[str, Any] = {
        "x": "x",
        "width": spec.width,
        "color": colors,
        "source": source,
        **kwargs,
    }
    # Same "only add legend_label when a label is actually set" guard as
    # ``plotmux.backends.bokeh.bar.render_bar`` (bokeh raises ``ValueError``
    # on a ``None`` entry, unlike matplotlib's silent no-op) -- here applied
    # per-series: an unlabeled series falls back to an empty string, same
    # as bokeh's own default for a legend-less renderer.
    if any(s.label is not None for s in spec.series):
        style.setdefault("legend_label", [s.label or "" for s in spec.series])
    # ``ALPHA`` (see ``plotmux.backends.bokeh.style``): bokeh's glyph
    # ``alpha`` rejects ``None`` outright, so it is only added when
    # ``spec.alpha`` is explicitly set.
    apply_fields(spec, [ALPHA], style)
    fig.vbar_stack(stackers, **style)
    return fig
