r"""Contain the plotly ``Backend`` implementation.

This module is only imported when plotly is installed (see
``plotmux.backends.plotly.__init__``), so it can import plotly
unconditionally.
"""

from __future__ import annotations

__all__ = ["PlotlyBackend", "trace_bars", "trace_line", "trace_points"]

import math
from html import escape
from typing import TYPE_CHECKING, Any, ClassVar

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.plotly.style import (
    DASH_STYLE,
    LEGEND_LOCATION,
    MARKER_STYLE,
    apply_legend,
    apply_style,
    rgba_to_plotly,
)
from plotmux.primitives import Bars, Line
from plotmux.scene import AxesScene, GridScene

if TYPE_CHECKING:
    from pathlib import Path

    from plotly.graph_objects import Figure

    from plotmux.primitives import Points, Primitive


def _legend_style(label: str | None, alpha: float | None) -> dict[str, Any]:
    r"""Return the trace options shared by every primitive.

    Args:
        label: The legend label, or ``None``.
        alpha: The opacity, or ``None``.

    Returns:
        The ``name``/``showlegend`` options when there is a label, and
            the ``opacity`` when there is an alpha.

    Example:
        ```pycon
        >>> from plotmux.backends.plotly.backend import _legend_style
        >>> _legend_style("a", 0.5)
        {'name': 'a', 'showlegend': True, 'opacity': 0.5}
        >>> _legend_style(None, None)
        {}

        ```
    """
    options: dict[str, Any] = {}
    if label is not None:
        options["name"] = label
        options["showlegend"] = True
    if alpha is not None:
        options["opacity"] = alpha
    return options


def trace_bars(bars: Bars) -> go.Bar:
    r"""Turn a ``Bars`` primitive into a plotly ``Bar`` trace.

    Args:
        bars: The bars to draw.

    Returns:
        The ``Bar`` trace, with the base of each bar.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.plotly.backend import trace_bars
        >>> from plotmux.primitives import Bars
        >>> trace_bars(Bars(x=np.arange(3.0), height=np.ones(3), base=np.zeros(3), width=0.8)).width
        0.8

        ```
    """
    return go.Bar(
        x=bars.x,
        y=bars.height,
        base=bars.base,
        width=bars.width,
        marker_color=None if bars.color is None else rgba_to_plotly(bars.color),
        **_legend_style(bars.label, bars.alpha),
    )


def trace_line(line: Line) -> go.Scatter:
    r"""Turn a ``Line`` primitive into a plotly ``Scatter`` trace.

    plotly has no infinite line: a slope is drawn as the segment of
    ``line.x``, ``line.y``.

    Args:
        line: The line to draw.

    Returns:
        The ``Scatter`` trace in ``"lines"`` mode.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.plotly.backend import trace_line
        >>> from plotmux.primitives import Line
        >>> trace_line(Line(x=np.arange(3.0), y=np.arange(3.0))).mode
        'lines'

        ```
    """
    style: dict[str, Any] = {"dash": DASH_STYLE[line.linestyle]}
    if line.color is not None:
        style["color"] = rgba_to_plotly(line.color)
    if line.linewidth is not None:
        style["width"] = line.linewidth
    return go.Scatter(
        x=line.x, y=line.y, mode="lines", line=style, **_legend_style(line.label, line.alpha)
    )


def trace_points(points: Points) -> go.Scatter:
    r"""Turn a ``Points`` primitive into a plotly ``Scatter`` trace.

    Args:
        points: The markers to draw.

    Returns:
        The ``Scatter`` trace in ``"markers"`` mode.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.plotly.backend import trace_points
        >>> from plotmux.primitives import Points
        >>> trace_points(Points(x=np.arange(3.0), y=np.arange(3.0))).mode
        'markers'

        ```
    """
    color = None if points.color is None else rgba_to_plotly(points.color)
    edgecolor = color if points.edgecolor is None else rgba_to_plotly(points.edgecolor)
    marker: dict[str, Any] = {}
    if color is not None:
        marker["color"] = color
    if points.size is not None:
        marker["size"] = points.size
    if edgecolor is not None:
        marker["line"] = {"color": edgecolor, "width": 1}
    if points.fill is False:
        marker["color"] = "rgba(0, 0, 0, 0)"
        marker.setdefault("line", {"color": color, "width": 1})
    if points.marker is not None:
        marker["symbol"] = MARKER_STYLE[points.marker]
    return go.Scatter(
        x=points.x,
        y=points.y,
        mode="markers",
        marker=marker,
        **_legend_style(points.label, points.alpha),
    )


def _trace(primitive: Primitive) -> go.Bar | go.Scatter:
    r"""Turn a primitive into a plotly trace.

    Args:
        primitive: The primitive to draw.

    Returns:
        The plotly trace.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.plotly.backend import _trace
        >>> from plotmux.primitives import Line
        >>> type(_trace(Line(x=np.arange(3.0), y=np.arange(3.0)))).__name__
        'Scatter'

        ```
    """
    if isinstance(primitive, Bars):
        return trace_bars(primitive)
    if isinstance(primitive, Line):
        return trace_line(primitive)
    return trace_points(primitive)


def _add_axes(
    fig: Figure, scene: AxesScene, *, row: int | None = None, col: int | None = None
) -> None:
    r"""Add the traces of a scene to a plotly ``Figure`` and style them.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        scene: The scene of one axes.
        row: The 1-indexed subplot row, or ``None``.
        col: The 1-indexed subplot column, or ``None``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> import plotly.graph_objects as go
        >>> from plotmux.backends.plotly.backend import _add_axes
        >>> from plotmux.primitives import Line
        >>> from plotmux.scene import AxesScene
        >>> fig = go.Figure()
        >>> _add_axes(fig, AxesScene(primitives=(Line(x=np.arange(3.0), y=np.arange(3.0)),)))
        >>> len(fig.data)
        1

        ```
    """
    for primitive in scene.primitives:
        fig.add_trace(_trace(primitive), row=row, col=col)
    apply_style(fig, scene, row=row, col=col)
    if scene.categories is not None:
        fig.update_xaxes(
            categoryorder="array", categoryarray=list(scene.categories), row=row, col=col
        )


class PlotlyBackend(Backend):
    r"""Implement the plotly rendering backend.

    A grid is one ``Figure`` of ``make_subplots``. plotly has one
    legend and one title per figure: a grid takes the legend style of
    its first panel that has a legend, and the title of the grid, while
    the title of each panel is a subplot title. The bars of a panel
    overlay each other (``barmode="overlay"``) and carry their own
    base, so a stacked bar is a stack of overlaid bars.
    """

    name: ClassVar[str] = "plotly"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"html", "json"}),
            grid_formats=frozenset({"html", "json"}),
            legend_locations=frozenset(LEGEND_LOCATION),
            markers=frozenset(MARKER_STYLE),
        )

    def draw(self, scene: AxesScene | GridScene) -> Figure:
        if not isinstance(scene, GridScene):
            fig = go.Figure()
            _add_axes(fig, scene)
            apply_legend(fig, scene)
            fig.update_layout(barmode="overlay")
            if scene.title is not None:
                fig.update_layout(title=scene.title)
            return fig
        nrows = math.ceil(len(scene.panels) / scene.ncols)
        fig = make_subplots(
            rows=nrows,
            cols=scene.ncols,
            subplot_titles=[escape(p.title) if p.title is not None else "" for p in scene.panels],
        )
        for i, panel in enumerate(scene.panels):
            _add_axes(fig, panel, row=i // scene.ncols + 1, col=i % scene.ncols + 1)
        for panel in scene.panels:
            if panel.legend is not None:
                apply_legend(fig, panel)
                break
        fig.update_layout(barmode="overlay")
        if scene.title is not None:
            fig.update_layout(title=scene.title)
        return fig

    def show(self, native: Figure) -> None:
        r"""Display a plotly ``Figure`` with ``Figure.show``.

        Args:
            native: The plotly ``Figure`` to display.
        """
        native.show()

    def save(self, native: Figure, path: Path, fmt: str) -> None:
        r"""Export a plotly ``Figure`` to a file.

        Args:
            native: The plotly ``Figure`` to export.
            path: The path where to save the figure.
            fmt: The export format, ``"html"`` or ``"json"``.
        """
        if fmt == "html":
            native.write_html(str(path))
        else:
            native.write_json(str(path))
