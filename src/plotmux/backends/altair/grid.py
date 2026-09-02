r"""Render a ``GridSpec`` into a concatenated altair ``ConcatChart``."""

from __future__ import annotations

__all__ = ["render_grid"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.bar import render_bar
from plotmux.backends.altair.cdf import render_cdf
from plotmux.backends.altair.histogram import render_histogram
from plotmux.backends.altair.layer import render_layer
from plotmux.backends.altair.line import render_line
from plotmux.backends.altair.scatter import render_scatter
from plotmux.backends.altair.style import apply_common_style
from plotmux.backends.base import resolve_renderer
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotmux.specs import GridSpec

# Reuses the per-type ``render_<type>(spec) -> alt.Chart`` functions, one
# entry per type also registered in ``AltairBackend._RENDERERS`` -- adding a
# new chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``). Includes
# ``LayerSpec`` (unlike ``plotmux.backends.altair.layer``'s own
# ``_MARK_RENDERERS``): a grid cell may itself be several series sharing one
# panel, since layering and gridding are independent, composable concerns --
# only a ``GridSpec`` nested inside another ``GridSpec`` is rejected (see
# ``GridSpec.__post_init__``).
_CELL_RENDERERS: dict[type[BaseSpec], Callable[..., alt.typing.ChartType]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    LayerSpec: render_layer,
}


def render_grid(spec: GridSpec, **kwargs: Any) -> alt.ConcatChart:
    r"""Render a ``GridSpec`` into a concatenated altair ``ConcatChart``.

    Each cell is rendered and styled independently -- via that cell's
    own ``render_<type>(cell)`` then ``apply_common_style`` -- exactly
    as a standalone chart would be (see ``AltairBackend._RENDERERS``),
    then all of them are combined with ``alt.concat(*charts,
    columns=spec.ncols)``, Vega-Lite's general-purpose layout operator
    for arranging independent views in a wrapping grid.

    Args:
        spec: The grid spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            cell's ``render_<type>`` call.

    Returns:
        The resulting ``ConcatChart``.

    Raises:
        NotImplementedError: if ``spec.cells`` contains a spec type
            with no altair renderer registered here.
    """
    charts = []
    for cell in spec.cells:
        renderer = resolve_renderer(_CELL_RENDERERS, cell, "altair")
        charts.append(apply_common_style(renderer(cell, **kwargs), cell))
    # ``alt.concat(*charts, columns=...)``'s return type is declared as
    # ``ConcatChart`` for this call shape; the cast mirrors
    # ``plotmux.backends.altair.layer.render_layer``'s own narrowing of
    # ``alt.layer(...)``'s broader declared return type.
    grid = cast("alt.ConcatChart", alt.concat(*charts, columns=spec.ncols))
    if spec.title is not None:
        grid = grid.properties(title=spec.title)
    return grid
