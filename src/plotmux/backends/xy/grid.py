r"""Render a ``GridSpec`` into a composed xy grid layout."""

from __future__ import annotations

__all__ = ["XyGrid", "render_grid", "render_grid_html"]

import html as _html
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from plotmux.backends.base import resolve_renderer
from plotmux.backends.xy.bar import render_bar
from plotmux.backends.xy.cdf import render_cdf
from plotmux.backends.xy.histogram import render_histogram
from plotmux.backends.xy.layer import render_layer
from plotmux.backends.xy.line import render_line
from plotmux.backends.xy.scatter import render_scatter
from plotmux.backends.xy.style import apply_common_style
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

    import xy

    from plotmux.specs import GridSpec

# Reuses the per-type ``render_<type>(spec) -> xy.Chart`` functions, one
# entry per type also registered in ``XyBackend._RENDERERS`` -- adding a new
# chart type there means adding one entry here too, following the same
# ``_RENDERERS``-dict pattern as every backend (see ``Backend``). Includes
# ``LayerSpec`` (unlike ``plotmux.backends.xy.layer``'s own
# ``_MARK_RENDERERS``): a grid cell may itself be several series sharing one
# panel, since layering and gridding are independent, composable concerns --
# only a ``GridSpec`` nested inside another ``GridSpec`` is rejected (see
# ``GridSpec.__post_init__``).
_CELL_RENDERERS: dict[type[BaseSpec], Callable[..., xy.Chart]] = {
    HistogramSpec: render_histogram,
    BarSpec: render_bar,
    CdfSpec: render_cdf,
    LineSpec: render_line,
    ScatterSpec: render_scatter,
    LayerSpec: render_layer,
}


@dataclass(frozen=True)
class XyGrid:
    r"""Hold the per-cell xy ``Chart``\ s composing one grid layout.

    Unlike the other three backends, xy has no chart-composition
    primitive suited to arranging independent, heterogeneous panels:
    ``xy.facet_chart`` repeats *one* mark composition once per value
    of a data column, it does not lay out arbitrary, already-built
    charts side by side (see ``XyBackend.save``, where this type is
    turned into an actual layout). This dataclass is therefore the
    native object ``render_grid`` returns for a ``GridSpec`` -- not an
    ``xy.Chart`` -- and ``XyBackend.save`` special-cases it rather than
    calling ``xy.Chart.write_image``/``write_html`` directly.

    Args:
        charts: The rendered, already-styled per-cell charts, in the
            same row-major order as ``GridSpec.cells``.
        ncols: The number of columns in the grid.
        title: An optional figure-level title, shown once above the
            whole grid.
    """

    charts: tuple[xy.Chart, ...]
    ncols: int
    title: str | None


def render_grid(spec: GridSpec, **kwargs: Any) -> XyGrid:
    r"""Render a ``GridSpec`` into an ``XyGrid``.

    Each cell is rendered and styled independently -- via that cell's
    own ``render_<type>(cell)`` then ``apply_common_style`` -- exactly
    as a standalone chart would be (see ``XyBackend._RENDERERS``), and
    the results are collected, unlayouted, into an ``XyGrid``. Actual
    panel layout only happens at export time, in ``XyBackend.save``
    (see ``XyGrid``'s docstring for why).

    Args:
        spec: The grid spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            cell's ``render_<type>`` call.

    Returns:
        The resulting ``XyGrid``.

    Raises:
        NotImplementedError: if ``spec.cells`` contains a spec type
            with no xy renderer registered here.
    """
    charts = []
    for cell in spec.cells:
        renderer = resolve_renderer(_CELL_RENDERERS, cell, "xy")
        charts.append(apply_common_style(renderer(cell, **kwargs), cell))
    return XyGrid(charts=tuple(charts), ncols=spec.ncols, title=spec.title)


def render_grid_html(grid: XyGrid) -> str:
    r"""Compose an ``XyGrid`` into one standalone HTML page.

    Each cell's own ``Chart.to_html()`` is already a full, self-
    contained document (its own ``<head>``, inline script/styles, a
    restrictive CSP -- see ``xy.Chart.to_html``), so cells cannot be
    concatenated as HTML fragments into one document without one
    cell's inline script or CSP clobbering another's. Instead, each
    cell's document is embedded in its own sandboxed ``<iframe
    srcdoc=...>``, and the iframes are arranged with CSS grid
    (``grid-template-columns: repeat(grid.ncols, 1fr)``) -- this is
    the actual "grid layout" ``XyGrid`` defers from render time to
    export time (see ``XyGrid``'s docstring).

    Args:
        grid: The grid to compose.

    Returns:
        A standalone HTML document with one iframe per cell.
    """
    nrows = math.ceil(len(grid.charts) / grid.ncols)
    panel_height = 420
    cells_html = "\n".join(
        f'<iframe class="plotmux-grid-cell" srcdoc="{_html.escape(chart.to_html())}"></iframe>'
        for chart in grid.charts
    )
    title_html = f"<h1>{_html.escape(grid.title)}</h1>" if grid.title is not None else ""
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 16px; font-family: sans-serif; }}
  .plotmux-grid {{
    display: grid;
    grid-template-columns: repeat({grid.ncols}, 1fr);
    grid-auto-rows: {panel_height}px;
    gap: 12px;
  }}
  .plotmux-grid-cell {{ width: 100%; height: 100%; border: none; }}
</style>
</head>
<body>
{title_html}
<div class="plotmux-grid" style="grid-template-rows: repeat({nrows}, {panel_height}px);">
{cells_html}
</div>
</body>
</html>
"""
