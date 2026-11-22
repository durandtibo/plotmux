r"""Contain the composed xy grid layout and its HTML."""

from __future__ import annotations

__all__ = ["XyGrid", "render_grid_html"]

import html as _html
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xy


@dataclass(frozen=True, slots=True)
class XyGrid:
    r"""Hold the per-cell xy ``Chart``\ s composing one grid layout.

    Unlike the other three backends, xy has no chart-composition
    primitive suited to arranging independent, heterogeneous panels:
    ``xy.facet_chart`` repeats *one* mark composition once per value
    of a data column, it does not lay out arbitrary, already-built
    charts side by side (see ``XyBackend.save``, where this type is
    turned into an actual layout). This dataclass is therefore the
    native object ``XyBackend.draw`` returns for a ``GridScene`` -- not an
    ``xy.Chart`` -- and ``XyBackend.save`` special-cases it rather than
    calling ``xy.Chart.write_image``/``write_html`` directly.

    Args:
        charts: The rendered, already-styled per-cell charts, in the
            same row-major order as ``GridScene.panels``.
        ncols: The number of columns in the grid.
        title: An optional figure-level title, shown once above the
            whole grid.
    """

    charts: tuple[xy.Chart, ...]
    ncols: int
    title: str | None


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
