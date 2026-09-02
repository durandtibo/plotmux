r"""Render a ``CdfSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_cdf"]

from typing import TYPE_CHECKING, Any

from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import CdfSpec


def render_cdf(ax: Axes, spec: CdfSpec, **kwargs: Any) -> Axes:
    r"""Render a ``CdfSpec`` onto a matplotlib ``Axes``.

    Uses matplotlib's own cumulative/step histogram support
    (``density=True, cumulative=True, histtype="step"``) rather than
    computing bin counts by hand -- unlike
    ``plotmux.backends.matplotlib.histogram.render_histogram``, which
    also relies on ``Axes.hist`` but for its regular, non-cumulative
    form.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The CDF spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.hist``. Overrides the spec-derived ``bins``/
            ``range``/``label``/``color`` when it repeats one of
            those keys (e.g. a shared ``color=`` passed to
            ``plotmux.layer``/``plotmux.grid``), instead of raising a
            ``TypeError`` for "multiple values for keyword argument".

    Returns:
        The ``Axes`` the CDF was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    style = {
        "bins": spec.nbins,
        "range": (xmin, xmax),
        "label": spec.label,
        "color": spec.color,
        "alpha": spec.alpha,
        "density": True,
        "cumulative": True,
        "histtype": "step",
        **kwargs,
    }
    ax.hist(spec.values, **style)
    if xmin < xmax:
        ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, 1)
    if spec.label is not None:
        ax.legend()
    return ax
