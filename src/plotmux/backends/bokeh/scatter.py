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
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``ScatterSpec.__post_init__``.
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
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    fig.scatter(x=spec.x, y=spec.y, fill_color=color, line_color=color, **kwargs)
    return fig
