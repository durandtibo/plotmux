r"""Render a ``HistogramSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any

from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import HistogramSpec


def render_histogram(ax: Axes, spec: HistogramSpec, **kwargs: Any) -> Axes:
    r"""Render a ``HistogramSpec`` onto a matplotlib ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The histogram spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.hist``. Overrides the spec-derived ``bins``/
            ``range``/``label``/``density``/``color`` when it repeats
            one of those keys (e.g. a shared ``density=`` passed to
            ``plotmux.layer``/``plotmux.grid``), instead of raising a
            ``TypeError`` for "multiple values for keyword argument".

    Returns:
        The ``Axes`` the histogram was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    style = {
        "bins": spec.bins,
        "range": (xmin, xmax),
        "label": spec.label,
        "density": spec.density,
        "color": spec.color,
        **kwargs,
    }
    ax.hist(spec.values, **style)
    if spec.label is not None:
        ax.legend()
    return ax
