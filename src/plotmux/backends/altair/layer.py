r"""Render a ``LayerSpec`` into a combined altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.cdf import render_cdf
from plotmux.backends.altair.histogram import render_histogram
from plotmux.backends.altair.line import render_line
from plotmux.backends.altair.scatter import render_scatter
from plotmux.backends.base import resolve_renderer
from plotmux.specs import BaseSpec, CdfSpec, HistogramSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotmux.specs import LayerSpec

# Reuses the per-type ``render_<type>(spec) -> alt.Chart`` functions, one
# entry per type also registered in ``AltairBackend._RENDERERS`` -- adding a
# new chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
_MARK_RENDERERS: dict[type[BaseSpec], Callable[..., alt.Chart]] = {
    HistogramSpec: render_histogram,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
}


def render_layer(spec: LayerSpec, **kwargs: Any) -> alt.LayerChart:
    r"""Render a ``LayerSpec`` into a combined altair ``LayerChart``.

    Unlike xy (see ``plotmux.backends.xy.layer``), altair *does* have
    a native chart-composition operator: ``chart_a + chart_b`` (sugar
    for ``alt.layer(chart_a, chart_b)``) builds a Vega-Lite
    ``LayerChart`` (this is the exception noted in
    ``plotmux.backends.xy.layer``'s own docstring). Each child spec is
    still rendered independently via its own ``render_<type>(spec)``
    -- the same functions used to render a standalone
    ``HistogramSpec``/``LineSpec``/``ScatterSpec`` -- and the results
    are combined via ``alt.layer(*charts)`` rather than each child's
    marks being merged manually the way xy's ``xy.chart(*marks)`` or
    matplotlib's shared ``Axes`` do. ``alt.layer(*charts)`` is used
    over ``functools.reduce(operator.add, charts)`` so a single-child
    ``LayerSpec`` still returns a ``LayerChart`` (``reduce`` over one
    element would return that element's own type, a plain ``Chart``,
    unchanged) -- every other backend's ``render_layer`` always
    returns its one combined-chart type regardless of child count, and
    this keeps that guarantee here too.

    Args:
        spec: The layer spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            child's ``render_<type>`` call.

    Returns:
        The resulting combined ``LayerChart``.

    Raises:
        NotImplementedError: if ``spec.layers`` contains a spec type
            with no altair renderer registered here.
    """
    charts = []
    for child in spec.layers:
        renderer = resolve_renderer(_MARK_RENDERERS, child, "altair")
        charts.append(renderer(child, **kwargs))
    # ``alt.layer(*charts)``'s overloads type its return as
    # ``LayerChart | FacetChart``, since one overload also accepts facet
    # arguments this call never passes -- every ``charts`` entry here is
    # always a plain ``Chart`` (from ``_MARK_RENDERERS``), so the result is
    # always a ``LayerChart``.
    #
    # ``resolve_scale(color="independent")``: Vega-Lite defaults to a
    # *shared* color scale across layers, so without this every layer's own
    # ``color`` encoding (each built by ``prepare_color`` against the same
    # field name, "label") gets merged into one scale and only the first
    # layer's color range survives -- every other backend renders each
    # child's own color correctly, so this keeps altair consistent with
    # them.
    return cast("alt.LayerChart", alt.layer(*charts).resolve_scale(color="independent"))
