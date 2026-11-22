r"""Contain the bokeh ``Backend`` implementation.

This module is only imported when bokeh is installed (see
``plotmux.backends.bokeh.__init__``), so it can import bokeh
unconditionally.
"""

from __future__ import annotations

__all__ = ["BokehBackend", "draw_bars", "draw_line", "draw_points"]

import math
from html import escape
from typing import TYPE_CHECKING, Any, ClassVar

from bokeh.io import show as bokeh_show
from bokeh.layouts import column, gridplot
from bokeh.models import Div, Slope, Title
from bokeh.plotting import figure as bokeh_figure, save as bokeh_save
from bokeh.resources import CDN

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.bokeh.style import LEGEND_LOCATIONS, MARKERS, apply_style, rgba_to_bokeh
from plotmux.primitives import Bars, Line
from plotmux.scene import AxesScene, GridScene

if TYPE_CHECKING:
    from pathlib import Path

    from bokeh.models import LayoutDOM, UIElement
    from bokeh.plotting import figure as Figure  # noqa: N812

    from plotmux.primitives import Points, Primitive


def draw_bars(fig: Figure, bars: Bars) -> None:
    r"""Draw a ``Bars`` primitive onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        bars: The bars to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.backend import draw_bars
        >>> from plotmux.primitives import Bars
        >>> fig = figure()
        >>> draw_bars(fig, Bars(x=np.arange(3.0), height=np.ones(3), base=np.zeros(3), width=0.8))
        >>> len(fig.renderers)
        1

        ```
    """
    style: dict[str, Any] = {}
    if bars.color is not None:
        style["fill_color"] = style["line_color"] = rgba_to_bokeh(bars.color)
    if bars.alpha is not None:
        style["alpha"] = bars.alpha
    if bars.label is not None:
        style["legend_label"] = bars.label
    fig.vbar(
        x=bars.x,
        bottom=bars.base,
        top=bars.base + bars.height,
        width=bars.width,
        **style,
    )


def draw_line(fig: Figure, line: Line) -> None:
    r"""Draw a ``Line`` primitive onto a bokeh ``figure``.

    A line with ``infinite`` set (a slope) is drawn with
    ``bokeh.models.Slope``, which keeps extending when the view changes.
    A ``Slope`` has no legend entry, so a labeled slope is drawn as the
    segment of its vertices. Any other line is a ``figure.line``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        line: The line to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.backend import draw_line
        >>> from plotmux.primitives import Line
        >>> fig = figure()
        >>> draw_line(fig, Line(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(fig.renderers)
        1

        ```
    """
    style: dict[str, Any] = {"line_dash": line.linestyle}
    if line.color is not None:
        style["line_color"] = rgba_to_bokeh(line.color)
    if line.linewidth is not None:
        style["line_width"] = line.linewidth
    if line.infinite is not None and line.label is None:
        gradient, intercept = line.infinite
        if line.alpha is not None:
            style["line_alpha"] = line.alpha
        fig.add_layout(Slope(gradient=gradient, y_intercept=intercept, **style))
        return
    if line.alpha is not None:
        style["alpha"] = line.alpha
    if line.label is not None:
        style["legend_label"] = line.label
    fig.line(x=line.x, y=line.y, **style)


def draw_points(fig: Figure, points: Points) -> None:
    r"""Draw a ``Points`` primitive onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        points: The markers to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.backend import draw_points
        >>> from plotmux.primitives import Points
        >>> fig = figure()
        >>> draw_points(fig, Points(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(fig.renderers)
        1

        ```
    """
    color = None if points.color is None else rgba_to_bokeh(points.color)
    edgecolor = color if points.edgecolor is None else rgba_to_bokeh(points.edgecolor)
    style: dict[str, Any] = {
        "fill_color": None if points.fill is False else color,
        "line_color": edgecolor,
    }
    if points.size is not None:
        style["size"] = points.size
    if points.alpha is not None:
        style["alpha"] = points.alpha
    if points.marker is not None:
        style["marker"] = points.marker
    if points.label is not None:
        style["legend_label"] = points.label
    fig.scatter(x=points.x, y=points.y, **style)


def _draw_primitive(fig: Figure, primitive: Primitive) -> None:
    r"""Draw one primitive onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        primitive: The primitive to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from bokeh.plotting import figure
        >>> from plotmux.backends.bokeh.backend import _draw_primitive
        >>> from plotmux.primitives import Line
        >>> fig = figure()
        >>> _draw_primitive(fig, Line(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(fig.renderers)
        1

        ```
    """
    if isinstance(primitive, Bars):
        draw_bars(fig, primitive)
    elif isinstance(primitive, Line):
        draw_line(fig, primitive)
    else:
        draw_points(fig, primitive)


def _draw_axes(scene: AxesScene) -> Figure:
    r"""Draw a scene into a styled bokeh ``figure``.

    The axis scales and a categorical x-range are construction-time
    arguments of ``bokeh.plotting.figure``, so the figure is created
    here, with the scales and the categories of the scene.

    Args:
        scene: The scene of one axes.

    Returns:
        The styled bokeh ``figure``.

    Example:
        ```pycon
        >>> from plotmux.backends.bokeh.backend import _draw_axes
        >>> from plotmux.scene import AxesScene
        >>> _draw_axes(AxesScene(primitives=(), title="t")).title.text
        't'

        ```
    """
    kwargs: dict[str, Any] = {"x_axis_type": scene.xscale, "y_axis_type": scene.yscale}
    if scene.categories is not None:
        kwargs = {"x_range": list(scene.categories), "y_axis_type": scene.yscale}
    fig = bokeh_figure(**kwargs)
    for primitive in scene.primitives:
        _draw_primitive(fig, primitive)
    return apply_style(fig, scene)


class BokehBackend(Backend):
    r"""Implement the bokeh rendering backend.

    A grid is a ``bokeh.layouts.gridplot`` of independent figures,
    under a heading ``Div`` when the grid has a title. bokeh exports
    to HTML only: static image export needs an extra, environment
    specific dependency.
    """

    name: ClassVar[str] = "bokeh"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"html"}),
            grid_formats=frozenset({"html"}),
            legend_locations=frozenset(LEGEND_LOCATIONS),
            markers=frozenset(MARKERS),
        )

    def draw(self, scene: AxesScene | GridScene) -> Figure | LayoutDOM:
        if not isinstance(scene, GridScene):
            return _draw_axes(scene)
        figs: list[UIElement | None] = [_draw_axes(panel) for panel in scene.panels]
        nrows = math.ceil(len(figs) / scene.ncols)
        rows = [figs[i * scene.ncols : (i + 1) * scene.ncols] for i in range(nrows)]
        grid = gridplot(rows)
        if scene.title is not None:
            return column(Div(text=f"<h2>{escape(scene.title)}</h2>"), grid)
        return grid

    def show(self, native: Figure | LayoutDOM) -> None:
        r"""Display a bokeh figure or layout with ``bokeh.io.show``.

        Args:
            native: The bokeh ``figure`` or layout to display.
        """
        bokeh_show(native)

    def save(self, native: Figure | LayoutDOM, path: Path, fmt: str) -> None:
        r"""Export a bokeh ``figure`` or layout to an HTML file.

        Args:
            native: The bokeh ``figure`` or layout to export.
            path: The path where to save the figure.
            fmt: The export format. Only ``"html"`` is supported (see
                ``capabilities``).
        """
        del fmt
        title = getattr(native, "title", None)
        title_text = str(title.text) if isinstance(title, Title) else title
        bokeh_save(
            native,
            filename=str(path),
            resources=CDN,
            title=title_text or "Bokeh Plot",
        )
