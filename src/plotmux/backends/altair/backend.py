r"""Contain the altair ``Backend`` implementation.

This module is only imported when altair is installed (see
``plotmux.backends.altair.__init__``), so it can import altair
unconditionally.
"""

from __future__ import annotations

__all__ = ["AltairBackend", "chart_bars", "chart_line", "chart_points"]

from typing import TYPE_CHECKING, Any, ClassVar, Literal, cast

import altair as alt
import numpy as np

from plotmux.backends.altair.style import (
    LEGEND_LOCATION,
    MARKER_STYLE,
    STROKE_DASH,
    axis_encodings,
    inline_data,
    legend_color,
    rgba_to_altair,
)
from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.primitives import Bars, Line
from plotmux.scene import AxesScene, GridScene

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.primitives import Points, Primitive


def _mark_chart(
    columns: dict[str, np.ndarray],
    mark: Literal["bar", "line", "point"],
    label: str | None,
    properties: dict[str, Any],
) -> alt.Chart:
    r"""Build a chart of one mark from columns.

    Args:
        columns: The columns of the inline data.
        mark: The mark type.
        label: The legend label, or ``None``. A label adds a constant
            ``"label"`` column bound to the legend color (see
            ``plotmux.backends.altair.style.legend_color``).
        properties: The mark properties, forwarded to ``alt.MarkDef``.

    Returns:
        The chart, with the mark and the data and no encoding yet.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.backend import _mark_chart
        >>> chart = _mark_chart({"x": np.array([0.0])}, "line", None, {"strokeWidth": 2})
        >>> chart.to_dict()["mark"]
        {'type': 'line', 'strokeWidth': 2}

        ```
    """
    if label is not None:
        n = len(next(iter(columns.values())))
        columns = {**columns, "label": np.full(n, label)}
    return alt.Chart(inline_data(columns), mark=alt.MarkDef(type=mark, **properties))


def chart_bars(bars: Bars, scene: AxesScene) -> alt.Chart:
    r"""Turn a ``Bars`` primitive into an altair chart.

    A numeric bar spans ``x - width / 2`` to ``x + width / 2`` (``x`` and
    ``x2``) and ``base`` to ``base + height`` (``y`` and ``y2``), so a bar
    has its own width and base. A categorical bar is a band, whose width
    is a fraction of the band.

    Args:
        bars: The bars to draw.
        scene: The scene of the axes, for the encodings.

    Returns:
        The chart of the bars.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.backend import chart_bars
        >>> from plotmux.primitives import Bars
        >>> from plotmux.scene import AxesScene
        >>> bars = Bars(x=np.arange(2.0), height=np.ones(2), base=np.zeros(2), width=0.8)
        >>> chart_bars(bars, AxesScene(primitives=(bars,))).to_dict()["mark"]["type"]
        'bar'

        ```
    """
    properties: dict[str, Any] = {}
    if bars.color is not None and bars.label is None:
        properties["color"] = rgba_to_altair(bars.color)
    if bars.alpha is not None:
        properties["opacity"] = bars.alpha
    top = bars.base + bars.height
    if bars.x.dtype.kind in "US":
        properties["width"] = alt.RelativeBandSize(float(cast("float", bars.width)))
        columns = {"x": bars.x, "y": top, "y2": bars.base}
        encodings = axis_encodings(scene)
    else:
        half = np.asarray(bars.width, dtype=float) / 2
        columns = {"x": bars.x - half, "x2": bars.x + half, "y": top, "y2": bars.base}
        encodings = axis_encodings(scene, x2_field="x2")
    chart = _mark_chart(columns, "bar", bars.label, properties).encode(
        **encodings, y2=alt.Y2("y2:Q")
    )
    color = legend_color(scene)
    return chart if bars.label is None or color is None else chart.encode(color=color)


def chart_line(line: Line, scene: AxesScene) -> alt.Chart:
    r"""Turn a ``Line`` primitive into an altair chart.

    altair has no infinite line: a slope is drawn as the segment of
    ``line.x``, ``line.y``.

    Args:
        line: The line to draw.
        scene: The scene of the axes, for the encodings.

    Returns:
        The chart of the line.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.backend import chart_line
        >>> from plotmux.primitives import Line
        >>> from plotmux.scene import AxesScene
        >>> line = Line(x=np.arange(3.0), y=np.arange(3.0))
        >>> chart_line(line, AxesScene(primitives=(line,))).to_dict()["mark"]["type"]
        'line'

        ```
    """
    properties: dict[str, Any] = {}
    if line.color is not None and line.label is None:
        properties["color"] = rgba_to_altair(line.color)
    if line.alpha is not None:
        properties["opacity"] = line.alpha
    if line.linewidth is not None:
        properties["strokeWidth"] = line.linewidth
    if line.linestyle in STROKE_DASH:
        properties["strokeDash"] = STROKE_DASH[line.linestyle]
    chart = _mark_chart({"x": line.x, "y": line.y}, "line", line.label, properties).encode(
        **axis_encodings(scene)
    )
    color = legend_color(scene)
    return chart if line.label is None or color is None else chart.encode(color=color)


def chart_points(points: Points, scene: AxesScene) -> alt.Chart:
    r"""Turn a ``Points`` primitive into an altair chart.

    Args:
        points: The markers to draw.
        scene: The scene of the axes, for the encodings.

    Returns:
        The chart of the markers.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.backend import chart_points
        >>> from plotmux.primitives import Points
        >>> from plotmux.scene import AxesScene
        >>> points = Points(x=np.arange(3.0), y=np.arange(3.0))
        >>> chart_points(points, AxesScene(primitives=(points,))).to_dict()["mark"]["type"]
        'point'

        ```
    """
    properties: dict[str, Any] = {}
    if points.color is not None and points.label is None:
        properties["color"] = rgba_to_altair(points.color)
    if points.size is not None:
        properties["size"] = points.size
    if points.alpha is not None:
        properties["opacity"] = points.alpha
    if points.edgecolor is not None:
        properties["filled"] = True
        properties["stroke"] = rgba_to_altair(points.edgecolor)
    if points.fill is False or points.marker == "x":
        # A hollow marker, and the cross (an open path): only the stroke shows.
        properties["filled"] = False
    if points.marker is not None:
        properties["shape"] = MARKER_STYLE[points.marker]
    chart = _mark_chart({"x": points.x, "y": points.y}, "point", points.label, properties).encode(
        **axis_encodings(scene)
    )
    color = legend_color(scene)
    return chart if points.label is None or color is None else chart.encode(color=color)


def _chart(primitive: Primitive, scene: AxesScene) -> alt.Chart:
    r"""Turn a primitive into an altair chart.

    Args:
        primitive: The primitive to draw.
        scene: The scene of the axes, for the encodings.

    Returns:
        The chart of the primitive.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.backend import _chart
        >>> from plotmux.primitives import Line
        >>> from plotmux.scene import AxesScene
        >>> line = Line(x=np.arange(3.0), y=np.arange(3.0))
        >>> _chart(line, AxesScene(primitives=(line,))).to_dict()["mark"]["type"]
        'line'

        ```
    """
    if isinstance(primitive, Bars):
        return chart_bars(primitive, scene)
    if isinstance(primitive, Line):
        return chart_line(primitive, scene)
    return chart_points(primitive, scene)


def _draw_axes(scene: AxesScene) -> alt.typing.ChartType:
    r"""Draw a scene into a styled altair chart.

    The charts of the primitives are layered, and the title and the
    background are properties of the layered chart.

    Args:
        scene: The scene of one axes.

    Returns:
        The altair chart or layered chart.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.backend import _draw_axes
        >>> from plotmux.scene import AxesScene
        >>> _draw_axes(AxesScene(primitives=(), title="t")).to_dict()["title"]
        't'

        ```
    """
    charts = [_chart(primitive, scene) for primitive in scene.primitives]
    chart: alt.typing.ChartType = (
        alt.layer(*charts) if len(charts) > 1 else charts[0] if charts else _empty_chart()
    )
    if scene.title is not None:
        chart = chart.properties(title=scene.title)
    if scene.background_color is not None:
        chart = chart.properties(
            view=alt.ViewBackground(fill=rgba_to_altair(scene.background_color))
        )
    return chart


def _empty_chart() -> alt.Chart:
    r"""Build the chart of an axes without primitive.

    Returns:
        A chart with no data point.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.backend import _empty_chart
        >>> _empty_chart().to_dict()["mark"]["type"]
        'point'

        ```
    """
    return alt.Chart(alt.Data(values=[]), mark=alt.MarkDef(type="point"))


class AltairBackend(Backend):
    r"""Implement the altair rendering backend.

    The data of each primitive is one CSV string (see
    ``plotmux.backends.altair.style.inline_data``), and the primitives
    of an axes are layered. A grid is an ``alt.concat``. altair exports
    to HTML and JSON only: static image export needs an extra,
    environment specific dependency.
    """

    name: ClassVar[str] = "altair"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"html", "json"}),
            grid_formats=frozenset({"html", "json"}),
            legend_locations=frozenset(LEGEND_LOCATION),
            markers=frozenset(MARKER_STYLE),
        )

    def draw(self, scene: AxesScene | GridScene) -> alt.typing.ChartType:
        if not isinstance(scene, GridScene):
            return _draw_axes(scene)
        grid = alt.concat(*(_draw_axes(panel) for panel in scene.panels), columns=scene.ncols)
        if scene.title is not None:
            grid = grid.properties(title=scene.title)
        return grid

    def show(self, native: alt.typing.ChartType) -> None:
        r"""Display an altair chart with ``Chart.show``.

        Args:
            native: The altair chart to display.
        """
        cast("Any", native).show()

    def save(self, native: alt.typing.ChartType, path: Path, fmt: str) -> None:
        r"""Export an altair chart to a file.

        Args:
            native: The altair chart to export.
            path: The path where to save the figure.
            fmt: The export format, ``"html"`` or ``"json"``.
        """
        cast("Any", native).save(str(path), format=cast("Literal['html', 'json']", fmt))
