r"""Apply the style of an ``AxesScene`` onto a matplotlib ``Axes``.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["LEGEND_LOCATION", "MARKER_STYLE", "apply_style"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.scene import AxesScene

#: The matplotlib ``loc`` of each portable legend location.
LEGEND_LOCATION = {
    "top_left": "upper left",
    "top_right": "upper right",
    "bottom_left": "lower left",
    "bottom_right": "lower right",
    "top": "upper center",
    "bottom": "lower center",
    "left": "center left",
    "right": "center right",
}

#: The matplotlib marker of each portable marker name.
MARKER_STYLE = {
    "circle": "o",
    "square": "s",
    "triangle": "^",
    "diamond": "D",
    "cross": "+",
    "x": "x",
}


def apply_style(ax: Axes, scene: AxesScene) -> Axes:
    r"""Apply the axes style of a scene onto an ``Axes``.

    Called once per axes, after the primitives are drawn. It applies
    the title, the labels, the scales, the background color, the
    limits and the legend.

    Args:
        ax: The matplotlib ``Axes`` to style.
        scene: The scene whose axes style to apply.

    Returns:
        The ``Axes`` that was styled.

    Example:
        ```pycon
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.style import apply_style
        >>> from plotmux.scene import AxesScene
        >>> ax = Figure().subplots()
        >>> apply_style(ax, AxesScene(primitives=(), title="t")).get_title()
        't'

        ```
    """
    if scene.title is not None:
        ax.set_title(scene.title)
    if scene.xlabel is not None:
        ax.set_xlabel(scene.xlabel)
    if scene.ylabel is not None:
        ax.set_ylabel(scene.ylabel)
    ax.set_xscale(scene.xscale)
    ax.set_yscale(scene.yscale)
    if scene.background_color is not None:
        ax.set_facecolor(scene.background_color)
    if scene.xlim != (None, None):
        ax.set_xlim(left=scene.xlim[0], right=scene.xlim[1])
    if scene.ylim != (None, None):
        ax.set_ylim(bottom=scene.ylim[0], top=scene.ylim[1])
    _apply_legend(ax, scene)
    return ax


def _apply_legend(ax: Axes, scene: AxesScene) -> None:
    r"""Draw the legend of a scene, if it has one.

    Args:
        ax: The matplotlib ``Axes`` that holds the labeled artists.
        scene: The scene whose legend style to apply.

    Example:
        ```pycon
        >>> from matplotlib.figure import Figure
        >>> from plotmux.backends.matplotlib.style import _apply_legend
        >>> from plotmux.scene import AxesScene
        >>> ax = Figure().subplots()
        >>> _apply_legend(ax, AxesScene(primitives=()))
        >>> ax.get_legend() is None
        True

        ```
    """
    if scene.legend is None:
        return
    kwargs: dict[str, object] = {}
    if scene.legend.title is not None:
        kwargs["title"] = scene.legend.title
    if scene.legend.location is not None:
        kwargs["loc"] = LEGEND_LOCATION[scene.legend.location]
    if scene.legend.orientation == "horizontal":
        kwargs["ncols"] = len(ax.get_legend_handles_labels()[0])
    ax.legend(**kwargs)
