r"""Render a ``SlopeSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_slope"]

from typing import TYPE_CHECKING, Any, cast

from bokeh.models import Slope

from plotmux.backends.bokeh.style import rgba_to_bokeh

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import SlopeSpec


def render_slope(fig: figure, spec: SlopeSpec, **kwargs: Any) -> figure:
    r"""Render a ``SlopeSpec`` onto a bokeh ``figure``.

    Uses ``bokeh.models.Slope``, bokeh's native annotation for a line
    defined by a gradient and a y-intercept, added via
    ``figure.add_layout`` rather than drawn as a glyph: unlike
    ``figure.line``, it spans the figure's current view regardless of
    data range, matching matplotlib's ``Axes.axline`` semantics (see
    ``plotmux.backends.matplotlib.slope.render_slope``).

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The slope spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``bokeh.models.Slope``. Overrides the spec-derived
            ``line_color``/``line_width``/``line_dash`` when it
            repeats one of those keys.

    Returns:
        The ``figure`` the line was added onto.
    """
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``SlopeSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.color))
    )
    # Unlike ``figure.line``'s ``line_color=None`` (a valid "use bokeh's
    # default" sentinel), ``Slope``'s ``line_width`` property is typed
    # ``Real`` and rejects ``None`` outright, so an unset field is left out
    # of the constructor call entirely rather than passed through as
    # ``None``, and bokeh's own default takes over.
    style: dict[str, Any] = {"line_dash": spec.linestyle}
    if color is not None:
        style["line_color"] = color
    if spec.linewidth is not None:
        style["line_width"] = spec.linewidth
    style.update(kwargs)
    # bokeh's ``Slope`` has no ``label``/legend integration of its own
    # (unlike a glyph's ``legend_label``): it is an annotation, not a
    # renderer entry, so ``spec.label`` has nothing to attach to here.
    fig.add_layout(Slope(gradient=spec.gradient, y_intercept=spec.intercept, **style))
    return fig
