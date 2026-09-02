r"""Render a ``SlopeSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_slope"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import SlopeSpec


def render_slope(ax: Axes, spec: SlopeSpec, **kwargs: Any) -> Axes:
    r"""Render a ``SlopeSpec`` onto a matplotlib ``Axes``.

    Uses ``Axes.axline``, matplotlib's native "line defined by a
    point and a slope, spanning the current view" primitive: unlike
    ``Axes.plot``, it draws correctly regardless of the axes' current
    or future data range (it keeps extending as the view changes),
    matching bokeh's ``Slope`` annotation semantics (see
    ``plotmux.backends.bokeh.slope.render_slope``).

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The slope spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.axline``. Overrides the spec-derived ``label``/
            ``color``/``linewidth``/``linestyle`` when it repeats one
            of those keys (e.g. a shared ``color=`` passed to
            ``plotmux.layer``/``plotmux.grid``), instead of raising a
            ``TypeError`` for "multiple values for keyword argument".

    Returns:
        The ``Axes`` the line was drawn onto.
    """
    style = {
        "label": spec.label,
        "color": spec.color,
        "linewidth": spec.linewidth,
        "linestyle": spec.linestyle,
        **kwargs,
    }
    ax.axline((0, spec.intercept), slope=spec.gradient, **style)
    if spec.label is not None:
        ax.legend()
    return ax
