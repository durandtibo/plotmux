r"""Contain the matplotlib ``Backend`` implementation.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["MatplotlibBackend", "draw_bars", "draw_line", "draw_points"]

import base64
import io
import math
from typing import TYPE_CHECKING, Any, ClassVar

from matplotlib import pyplot
from matplotlib.figure import Figure as MplFigure

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.backends.matplotlib.style import LEGEND_LOCATION, MARKER_STYLE, apply_style
from plotmux.primitives import Bars, Line, Points
from plotmux.scene import AxesScene, GridScene

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.axes import Axes

    from plotmux.primitives import Primitive


def draw_bars(ax: Axes, bars: Bars) -> None:
    r"""Draw a ``Bars`` primitive onto an ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        bars: The bars to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.backend import draw_bars
        >>> from plotmux.primitives import Bars
        >>> ax = Figure().subplots()
        >>> draw_bars(ax, Bars(x=np.arange(3.0), height=np.ones(3), base=np.zeros(3), width=0.8))
        >>> len(ax.patches)
        3

        ```
    """
    ax.bar(
        bars.x,
        bars.height,
        width=bars.width,
        bottom=bars.base,
        color=bars.color,
        alpha=bars.alpha,
        label=bars.label,
    )


def draw_line(ax: Axes, line: Line) -> None:
    r"""Draw a ``Line`` primitive onto an ``Axes``.

    A line with ``infinite`` set (a slope) is drawn with ``Axes.axline``,
    which keeps extending when the view changes. Any other line is a
    ``Axes.plot`` of its vertices.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        line: The line to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.backend import draw_line
        >>> from plotmux.primitives import Line
        >>> ax = Figure().subplots()
        >>> draw_line(ax, Line(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(ax.lines)
        1

        ```
    """
    style: dict[str, Any] = {
        "color": line.color,
        "alpha": line.alpha,
        "linewidth": line.linewidth,
        "linestyle": line.linestyle,
        "label": line.label,
    }
    if line.infinite is not None:
        gradient, intercept = line.infinite
        ax.axline((0, intercept), slope=gradient, **style)
    else:
        ax.plot(line.x, line.y, **style)


def draw_points(ax: Axes, points: Points) -> None:
    r"""Draw a ``Points`` primitive onto an ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        points: The markers to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.backend import draw_points
        >>> from plotmux.primitives import Points
        >>> ax = Figure().subplots()
        >>> draw_points(ax, Points(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(ax.collections)
        1

        ```
    """
    style: dict[str, Any] = {"alpha": points.alpha, "s": points.size, "label": points.label}
    if points.marker is not None:
        style["marker"] = MARKER_STYLE[points.marker]
    if points.fill is False:
        style["facecolors"] = "none"
        style["edgecolors"] = points.edgecolor if points.edgecolor is not None else points.color
    else:
        style["color"] = points.color
        if points.edgecolor is not None:
            style["edgecolors"] = points.edgecolor
    ax.scatter(points.x, points.y, **style)


def _draw_primitive(ax: Axes, primitive: Primitive) -> None:
    r"""Draw one primitive onto an ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        primitive: The primitive to draw.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.backend import _draw_primitive
        >>> from plotmux.primitives import Line
        >>> ax = Figure().subplots()
        >>> _draw_primitive(ax, Line(x=np.arange(3.0), y=np.arange(3.0)))
        >>> len(ax.lines)
        1

        ```
    """
    if isinstance(primitive, Bars):
        draw_bars(ax, primitive)
    elif isinstance(primitive, Line):
        draw_line(ax, primitive)
    else:
        draw_points(ax, primitive)


def _draw_axes(ax: Axes, scene: AxesScene) -> None:
    r"""Draw the primitives of a scene onto an ``Axes`` and style it.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        scene: The scene of one axes.

    Example:
        ```pycon
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.backend import _draw_axes
        >>> from plotmux.scene import AxesScene
        >>> ax = Figure().subplots()
        >>> _draw_axes(ax, AxesScene(primitives=(), title="t"))
        >>> ax.get_title()
        't'

        ```
    """
    for primitive in scene.primitives:
        _draw_primitive(ax, primitive)
    apply_style(ax, scene)


class MatplotlibBackend(Backend):
    r"""Implement the matplotlib rendering backend.

    The figure is built with the ``matplotlib.figure.Figure``
    constructor rather than ``pyplot.subplots()``: the latter registers
    the figure with pyplot's global figure manager, so figures created
    that way are never garbage-collected until ``plt.close()`` is called
    on them explicitly, a real memory leak for code that renders many
    figures. A figure built directly is a plain, independently garbage-
    collectable object.
    """

    name: ClassVar[str] = "matplotlib"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"png", "svg", "pdf", "jpg", "jpeg"}),
            grid_formats=frozenset({"png", "svg", "pdf", "jpg", "jpeg"}),
            legend_locations=frozenset(LEGEND_LOCATION),
            markers=frozenset(MARKER_STYLE),
        )

    def draw(self, scene: AxesScene | GridScene) -> MplFigure:
        fig = MplFigure()
        if isinstance(scene, GridScene):
            nrows = math.ceil(len(scene.panels) / scene.ncols)
            axes = fig.subplots(nrows, scene.ncols, squeeze=False)
            flat_axes = [ax for row in axes for ax in row]
            for ax, panel in zip(flat_axes, scene.panels, strict=False):
                _draw_axes(ax, panel)
            for ax in flat_axes[len(scene.panels) :]:
                ax.set_visible(False)
            if scene.title is not None:
                fig.suptitle(scene.title)
        else:
            _draw_axes(fig.subplots(), scene)
        return fig

    def show(self, native: MplFigure) -> None:
        r"""Display a matplotlib ``Figure`` in a window.

        The figure is built without pyplot, so it has no figure
        manager and ``Figure.show`` raises. This gives it the manager
        of a new pyplot figure, then calls ``pyplot.show``, which
        blocks in a script until the window is closed. With a
        non-interactive matplotlib backend (e.g. ``Agg``), matplotlib
        only emits a ``UserWarning``.

        Args:
            native: The matplotlib ``Figure`` to display.
        """
        canvas = pyplot.figure().canvas
        canvas.figure = native
        native.set_canvas(canvas)
        pyplot.show()

    def mimebundle(self, native: MplFigure) -> dict[str, Any] | None:
        r"""Return the PNG of a matplotlib ``Figure`` for Jupyter.

        ``Figure.savefig`` works on a figure built without pyplot, so
        no canvas is attached to the figure.

        Args:
            native: The matplotlib ``Figure`` to display.

        Returns:
            A dict with the base64 encoded PNG as ``"image/png"``.
        """
        buffer = io.BytesIO()
        native.savefig(buffer, format="png")
        return {"image/png": base64.b64encode(buffer.getvalue()).decode("ascii")}

    def save(self, native: MplFigure, path: Path, fmt: str) -> None:
        native.savefig(path, format=fmt)
