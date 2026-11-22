r"""Contain the xy ``Backend`` implementation.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["XyBackend", "mark_bars", "mark_line", "mark_points"]

import tempfile
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import xy

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.xy.grid import XyGrid, render_grid_html
from plotmux.backends.xy.style import LEGEND_LOCATION, MARKERS, apply_style, rgba_to_xy
from plotmux.primitives import Bars, Line
from plotmux.scene import AxesScene, GridScene

if TYPE_CHECKING:
    from plotmux.primitives import Points, Primitive


def mark_bars(bars: Bars) -> xy.Mark:
    r"""Turn a ``Bars`` primitive into an xy mark.

    Args:
        bars: The bars to draw.

    Returns:
        The xy ``bar`` mark.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.xy.backend import mark_bars
        >>> from plotmux.primitives import Bars
        >>> mark_bars(Bars(x=np.arange(3.0), height=np.ones(3), base=np.zeros(3), width=0.8)).kind
        'bar'

        ```
    """
    kwargs: dict[str, Any] = {}
    if bars.alpha is not None:
        kwargs["opacity"] = bars.alpha
    return xy.bar(
        bars.x,
        bars.height,
        width=bars.width,
        base=bars.base,
        name=bars.label,
        color=None if bars.color is None else rgba_to_xy(bars.color),
        **kwargs,
    )


def mark_line(line: Line) -> xy.Mark:
    r"""Turn a ``Line`` primitive into an xy mark.

    xy has no infinite line: a slope is drawn as the segment of
    ``line.x``, ``line.y``.

    Args:
        line: The line to draw.

    Returns:
        The xy ``line`` mark.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.xy.backend import mark_line
        >>> from plotmux.primitives import Line
        >>> mark_line(Line(x=np.arange(3.0), y=np.arange(3.0))).kind
        'line'

        ```
    """
    kwargs: dict[str, Any] = {}
    if line.alpha is not None:
        kwargs["opacity"] = line.alpha
    if line.linewidth is not None:
        kwargs["width"] = line.linewidth
    if line.linestyle != "solid":
        kwargs["dash"] = line.linestyle
    return xy.line(
        line.x,
        line.y,
        name=line.label,
        color=None if line.color is None else rgba_to_xy(line.color),
        **kwargs,
    )


def mark_points(points: Points) -> xy.Mark:
    r"""Turn a ``Points`` primitive into an xy mark.

    Args:
        points: The markers to draw.

    Returns:
        The xy ``scatter`` mark.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.xy.backend import mark_points
        >>> from plotmux.primitives import Points
        >>> mark_points(Points(x=np.arange(3.0), y=np.arange(3.0))).kind
        'scatter'

        ```
    """
    color = None if points.color is None else rgba_to_xy(points.color)
    kwargs: dict[str, Any] = {}
    if points.size is not None:
        kwargs["size"] = points.size
    if points.alpha is not None:
        kwargs["opacity"] = points.alpha
    if points.edgecolor is not None:
        kwargs["stroke"] = rgba_to_xy(points.edgecolor)
        kwargs["stroke_width"] = 1.0
    if points.fill is False:
        kwargs.setdefault("stroke", color)
        kwargs["stroke_width"] = 1.0
        color = "rgba(0, 0, 0, 0)"
    if points.marker is not None:
        kwargs["symbol"] = points.marker
    return xy.scatter(points.x, points.y, name=points.label, color=color, **kwargs)


def _mark(primitive: Primitive) -> xy.Mark:
    r"""Turn a primitive into an xy mark.

    Args:
        primitive: The primitive to draw.

    Returns:
        The xy mark.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.xy.backend import _mark
        >>> from plotmux.primitives import Line
        >>> _mark(Line(x=np.arange(3.0), y=np.arange(3.0))).kind
        'line'

        ```
    """
    if isinstance(primitive, Bars):
        return mark_bars(primitive)
    if isinstance(primitive, Line):
        return mark_line(primitive)
    return mark_points(primitive)


def _draw_axes(scene: AxesScene) -> xy.Chart:
    r"""Draw the primitives of a scene into a styled xy ``Chart``.

    Args:
        scene: The scene of one axes.

    Returns:
        The xy ``Chart``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.xy.backend import _draw_axes
        >>> from plotmux.primitives import Line
        >>> from plotmux.scene import AxesScene
        >>> scene = AxesScene(primitives=(Line(x=np.arange(3.0), y=np.arange(3.0)),), title="t")
        >>> _draw_axes(scene).title
        't'

        ```
    """
    return apply_style(xy.chart(*(_mark(p) for p in scene.primitives)), scene)


class XyBackend(Backend):
    r"""Implement the xy rendering backend.

    A figure is an ``xy.Chart`` and a grid is an ``XyGrid`` of charts
    (see ``plotmux.backends.xy.grid``), which can only be exported to
    HTML: xy has no chart-composition primitive for arranging
    independent panels into one PNG/SVG/PDF.
    """

    name: ClassVar[str] = "xy"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"png", "jpg", "jpeg", "webp", "svg", "pdf", "html"}),
            grid_formats=frozenset({"html"}),
            legend_locations=frozenset(LEGEND_LOCATION),
            markers=frozenset(MARKERS),
        )

    def draw(self, scene: AxesScene | GridScene) -> xy.Chart | XyGrid:
        if isinstance(scene, GridScene):
            return XyGrid(
                charts=tuple(_draw_axes(panel) for panel in scene.panels),
                ncols=scene.ncols,
                title=scene.title,
            )
        return _draw_axes(scene)

    def show(self, native: xy.Chart | XyGrid) -> None:
        r"""Display an xy ``Chart`` or ``XyGrid`` in the web browser.

        The HTML of the figure is written to a temporary file that is
        opened with ``webbrowser.open``.

        Args:
            native: The xy ``Chart`` or ``XyGrid`` to display.
        """
        html = self._html(native)
        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        ) as file:
            file.write(html)
        webbrowser.open(Path(file.name).as_uri())

    def mimebundle(self, native: xy.Chart | XyGrid) -> dict[str, Any] | None:
        r"""Return the HTML of an xy ``Chart`` or ``XyGrid`` for Jupyter.

        Args:
            native: The xy ``Chart`` or ``XyGrid`` to display.

        Returns:
            A dict with the HTML as ``"text/html"``.
        """
        return {"text/html": self._html(native)}

    @staticmethod
    def _html(native: xy.Chart | XyGrid) -> str:
        r"""Return the standalone HTML of an xy ``Chart`` or ``XyGrid``.

        Args:
            native: The xy ``Chart`` or ``XyGrid``.

        Returns:
            The HTML document.
        """
        if isinstance(native, XyGrid):
            return render_grid_html(native)
        return native._repr_html_()

    def save(self, native: xy.Chart | XyGrid, path: Path, fmt: str) -> None:
        r"""Export an xy ``Chart`` or ``XyGrid`` to a file.

        Args:
            native: The xy ``Chart`` or ``XyGrid`` to export.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``,
                ``"html"``).

        Raises:
            UnsupportedFormatError: if ``native`` is an ``XyGrid`` and
                ``fmt`` is not ``"html"``. Also a ``ValueError``.
        """
        if isinstance(native, XyGrid):
            self.capabilities().check_format(fmt, grid=True)
            path.write_text(render_grid_html(native), encoding="utf-8")
        else:
            native.write_image(path, format=fmt)
