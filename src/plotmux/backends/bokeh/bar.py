r"""Render a ``BarSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_bar"]

from typing import TYPE_CHECKING, Any, cast

from plotmux.backends.bokeh.style import rgba_to_bokeh

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import BarSpec


def render_bar(fig: figure, spec: BarSpec, **kwargs: Any) -> figure:
    r"""Render a ``BarSpec`` onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.vbar``.

    Returns:
        The ``figure`` the bars were drawn onto.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``BarSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.color))
    )
    # bokeh raises ``ValueError`` if ``legend_label`` is passed as ``None``
    # (unlike matplotlib's ``label=None``, which is a silent no-op), so the
    # kwarg is only added when a label is actually set.
    if spec.label is not None:
        kwargs.setdefault("legend_label", spec.label)
    style: dict[str, Any] = {"width": spec.width, **kwargs}
    if color is not None:
        style.setdefault("fill_color", color)
        style.setdefault("line_color", color)
    # bokeh's glyph ``alpha`` property rejects ``None`` outright, so it is
    # only added when ``spec.alpha`` is explicitly set (see
    # ``plotmux.backends.bokeh.histogram.render_histogram``).
    if spec.alpha is not None:
        style.setdefault("alpha", spec.alpha)
    fig.vbar(x=spec.x, top=spec.y, **style)
    return fig
