r"""Apply the common figure-level style fields onto a bokeh ``figure``.

This module is only imported when bokeh is installed (see
``plotmux.backends.bokeh.__init__``), so it can import bokeh
unconditionally.
"""

from __future__ import annotations

__all__ = ["apply_common_style", "rgba_to_bokeh"]

from typing import TYPE_CHECKING

from bokeh.colors import RGB

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import BaseSpec


def rgba_to_bokeh(color: tuple[float, float, float, float]) -> RGB:
    r"""Convert a canonical RGBA tuple to bokeh's native color type.

    bokeh's glyph color parameters (e.g. ``line_color``, ``fill_color``)
    accept a ``bokeh.colors.RGB`` instance, so the canonical ``[0, 1]``
    float RGBA tuple produced by ``plotmux.colors.parse_color`` is
    converted to that format here rather than in ``core/``, keeping
    ``core/`` free of any single backend's native color representation
    -- same pattern as ``plotmux.backends.xy.style.rgba_to_xy``.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a ``bokeh.colors.RGB``, with ``r``/``g``/``b`` as
            integers in ``[0, 255]`` and ``a`` as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.bokeh.style import rgba_to_bokeh
        >>> rgba_to_bokeh((1.0, 0.0, 0.0, 1.0))
        rgb(255, 0, 0)

        ```
    """
    r, g, b, a = color
    return RGB(round(r * 255), round(g * 255), round(b * 255), a)


def apply_common_style(fig: figure, spec: BaseSpec) -> figure:
    r"""Apply the common figure-level style fields onto a bokeh
    ``figure``.

    Applies ``title``/``xlabel``/``ylabel`` from ``spec`` (defined on
    ``BaseSpec``, shared by every chart type). Called once per
    backend, right after the chart-specific renderer has drawn its
    glyph, so a new chart type gets title/label support for free.

    Unlike matplotlib's ``Axes.set_xscale``, bokeh's axis type
    (``"linear"``/``"log"``) is a construction-time argument of
    ``bokeh.plotting.figure`` (``x_axis_type``/``y_axis_type``), not a
    mutable property that can be flipped after glyphs are added -- so
    ``spec.xscale``/``spec.yscale`` are applied where the figure is
    created (``backends/bokeh/backend.py::_make_renderer``), not here.

    Args:
        fig: The bokeh ``figure`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The ``figure`` that was styled.
    """
    if spec.title is not None:
        fig.title = spec.title
    if spec.xlabel is not None:
        fig.xaxis.axis_label = spec.xlabel
    if spec.ylabel is not None:
        fig.yaxis.axis_label = spec.ylabel
    return fig
