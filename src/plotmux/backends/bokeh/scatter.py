r"""Render a ``ScatterSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

from plotmux.backends.bokeh.style import rgba_to_bokeh

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import ScatterSpec


def render_scatter(fig: figure, spec: ScatterSpec, **kwargs: Any) -> figure:
    r"""Render a ``ScatterSpec`` onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.scatter``.

    Returns:
        The ``figure`` the markers were drawn onto.
    """
    # ``spec.color``/``spec.edgecolor``, once set, are already canonical
    # RGBA tuples: they went through ``parse_color`` in
    # ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.color))
    )
    edgecolor = (
        color
        if spec.edgecolor is None
        else rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.edgecolor))
    )
    # bokeh raises ``ValueError`` if ``legend_label`` is passed as ``None``
    # (unlike matplotlib's ``label=None``, which is a silent no-op), so the
    # kwarg is only added when a label is actually set.
    if spec.label is not None:
        kwargs.setdefault("legend_label", spec.label)
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    # bokeh's glyph ``alpha`` property rejects ``None`` outright, so it is
    # only added when ``spec.alpha`` is explicitly set (see
    # ``plotmux.backends.bokeh.histogram.render_histogram``).
    if spec.alpha is not None:
        kwargs.setdefault("alpha", spec.alpha)
    # bokeh's ``figure.scatter(marker=...)`` accepts plotmux's portable
    # shape names directly (``"circle"``/``"square"``/``"triangle"``/
    # ``"diamond"``/``"cross"``/``"x"``), unlike matplotlib, so no
    # translation table is needed here (see
    # ``plotmux.backends.matplotlib.scatter.MARKER_STYLE``).
    if spec.marker is not None:
        kwargs.setdefault("marker", spec.marker)
    fig.scatter(x=spec.x, y=spec.y, fill_color=color, line_color=edgecolor, **kwargs)
    return fig
