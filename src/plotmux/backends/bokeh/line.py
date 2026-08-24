r"""Render a ``LineSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_line"]

from typing import TYPE_CHECKING, Any, cast

from plotmux.backends.bokeh.style import rgba_to_bokeh

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import LineSpec


def render_line(fig: figure, spec: LineSpec, **kwargs: Any) -> figure:
    r"""Render a ``LineSpec`` onto a bokeh ``figure``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The line spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.line``.

    Returns:
        The ``figure`` the line was drawn onto.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``LineSpec.__post_init__``.
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
    fig.line(x=spec.x, y=spec.y, line_color=color, **kwargs)
    return fig
