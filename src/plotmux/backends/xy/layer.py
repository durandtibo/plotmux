r"""Render a ``LayerSpec`` into a combined xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_layer"]

from typing import TYPE_CHECKING, Any

import xy

from plotmux.backends.base import resolve_renderer
from plotmux.backends.xy.bar import render_bar
from plotmux.backends.xy.cdf import render_cdf
from plotmux.backends.xy.histogram import render_histogram
from plotmux.backends.xy.line import render_line
from plotmux.backends.xy.scatter import render_scatter
from plotmux.specs import BarSpec, BaseSpec, CdfSpec, HistogramSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotmux.specs import LayerSpec

# Reuses the per-type ``render_<type>(spec) -> xy.Chart`` functions, one
# entry per type also registered in ``XyBackend._RENDERERS`` -- adding a
# new chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``).
_MARK_RENDERERS: dict[type[BaseSpec], Callable[..., xy.Chart]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
}


def render_layer(spec: LayerSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``LayerSpec`` into a combined xy ``Chart``.

    xy's ``Chart`` has no chart-composition operator (no ``chart_a +
    chart_b``, unlike Altair), so each child spec is rendered
    independently via its own ``render_<type>(child_spec)`` -- the
    same functions used to render a standalone
    ``HistogramSpec``/``LineSpec``/``ScatterSpec`` -- and only its
    mark children are kept (each per-type renderer returns a
    single-mark ``Chart`` with no axes yet; axes are added once, for
    the combined chart, by ``apply_common_style``). Those marks are
    combined into one ``Chart`` via ``xy.chart(*marks)``, xy's
    generic multi-mark composer.

    Args:
        spec: The layer spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            child's ``render_<type>`` call.

    Returns:
        The resulting combined xy ``Chart``.

    Raises:
        NotImplementedError: if ``spec.layers`` contains a spec type
            with no xy renderer registered here.
    """
    marks: list[Any] = []
    for child in spec.layers:
        renderer = resolve_renderer(_MARK_RENDERERS, child, "xy")
        marks.extend(renderer(child, **kwargs).children)
    return xy.chart(*marks)
