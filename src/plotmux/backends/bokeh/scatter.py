r"""Render a ``ScatterSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

from plotmux.backends.bokeh.style import (
    ALPHA,
    LABEL,
    MARKER,
    SIZE,
    apply_fields,
    rgba_to_bokeh,
)

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
    # ``fill_color=None`` is bokeh's own native hollow-marker spelling: an
    # unset ``fill_color`` already renders transparent on this backend
    # (unlike every other one, whose default fill is opaque -- see
    # ``ScatterSpec.fill``'s docstring), so ``spec.fill is False`` simply
    # forces the fill to ``None`` explicitly rather than leaving it to
    # ``color``.
    if spec.fill is False:
        color = None
    # ``LABEL``/``SIZE``/``ALPHA``/``MARKER`` (see
    # ``plotmux.backends.bokeh.style``): bokeh raises ``ValueError`` on
    # ``legend_label=None`` and rejects ``alpha=None`` outright, so both are
    # only added when explicitly set; ``marker`` accepts plotmux's portable
    # shape names directly, unlike matplotlib (see
    # ``plotmux.backends.matplotlib.scatter.MARKER_STYLE``).
    apply_fields(spec, [LABEL, SIZE, ALPHA, MARKER], kwargs)
    fig.scatter(x=spec.x, y=spec.y, fill_color=color, line_color=edgecolor, **kwargs)
    return fig
