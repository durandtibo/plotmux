r"""Render a ``StackedBarSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_stacked_bar"]

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import StackedBarSpec


def render_stacked_bar(ax: Axes, spec: StackedBarSpec, **kwargs: Any) -> Axes:
    r"""Render a ``StackedBarSpec`` onto a matplotlib ``Axes``.

    Draws one ``Axes.bar`` call per series, each with ``bottom=``
    the running total of every series drawn before it -- matplotlib's
    own idiom for a stacked bar (it has no native stacking primitive,
    unlike bokeh's ``vbar_stack``).

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The stacked-bar spec to render.
        **kwargs: Additional keyword arguments forwarded to every
            ``Axes.bar`` call.

    Returns:
        The ``Axes`` the bars were drawn onto.
    """
    bottom = None
    for series in spec.series:
        style = {
            "width": spec.width,
            "label": series.label,
            "color": cast("tuple[float, float, float, float]", series.color),
            "alpha": spec.alpha,
            "bottom": bottom,
            **kwargs,
        }
        ax.bar(spec.x, series.y, **style)
        bottom = series.y if bottom is None else bottom + series.y
    if any(series.label is not None for series in spec.series):
        ax.legend()
    return ax
