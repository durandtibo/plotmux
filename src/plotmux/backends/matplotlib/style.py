r"""Apply the common figure-level style fields onto a matplotlib
``Axes``.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["apply_common_style", "attach_repr_png"]

import io
from typing import TYPE_CHECKING

from matplotlib.backends.backend_agg import FigureCanvasAgg

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure as MplFigure

    from plotmux.specs import BaseSpec


def apply_common_style(ax: Axes, spec: BaseSpec) -> Axes:
    r"""Apply the common figure-level style fields onto an ``Axes``.

    Applies ``title``/``xlabel``/``ylabel``/``xscale``/``yscale`` from
    ``spec`` (defined on ``BaseSpec``, shared by every chart type).
    Called once per backend, right after the chart-specific renderer
    has drawn its mark, so a new chart type gets title/label/scale
    support for free.

    Args:
        ax: The matplotlib ``Axes`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The ``Axes`` that was styled.
    """
    if spec.title is not None:
        ax.set_title(spec.title)
    if spec.xlabel is not None:
        ax.set_xlabel(spec.xlabel)
    if spec.ylabel is not None:
        ax.set_ylabel(spec.ylabel)
    ax.set_xscale(spec.xscale)
    ax.set_yscale(spec.yscale)
    return ax


def attach_repr_png(fig: MplFigure) -> None:
    r"""Attach a working ``_repr_png_`` to a bare ``Figure``.

    A ``Figure`` built via the constructor directly (rather than
    ``pyplot.subplots()``, see ``plotmux.backends.matplotlib.backend``'s
    module docstring for why) gets a plain ``FigureCanvasBase``, which
    has no ``print_png``: only a concrete backend canvas (e.g. Agg)
    does. Jupyter, though, displays the last expression of a cell via
    ``_repr_png_``/``_repr_html_``/etc looked up on the object itself
    -- and outside ``%matplotlib inline`` (which patches things at
    the pyplot level, not on individual ``Figure`` instances),
    ``Figure`` defines neither. Attaching a bound ``_repr_png_`` here,
    once, right after a figure is fully drawn and styled, is what lets
    ``plotmux.Figure._repr_png_`` (see ``plotmux.figure``) simply
    forward to it and get a real PNG in any notebook, with no
    ``%matplotlib inline`` required.

    Called from both ``backend.py`` (one chart's ``Figure``) and
    ``grid.py`` (a ``GridSpec``'s combined ``Figure``) right before
    each returns, so every matplotlib-backed ``Figure`` gets this for
    free regardless of which spec type produced it.

    Swapping in an ``Agg`` canvas is safe even for a figure that will
    also be shown interactively later (e.g. via ``Figure.show()``):
    matplotlib canvases are freely replaceable on a ``Figure``, and
    Agg is a raster backend with no GUI event loop of its own to
    conflict with one.

    Args:
        fig: The matplotlib ``Figure`` to attach ``_repr_png_`` to.
    """
    canvas = FigureCanvasAgg(fig)

    def _repr_png_() -> bytes:
        buffer = io.BytesIO()
        canvas.print_png(buffer)
        return buffer.getvalue()

    fig._repr_png_ = _repr_png_  # type: ignore[attr-defined]
