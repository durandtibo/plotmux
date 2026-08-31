r"""Render a ``CdfSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_cdf"]

from typing import TYPE_CHECKING, Any, cast

from bokeh.models import Range1d

from plotmux.backends.bokeh.style import rgba_to_bokeh
from plotmux.utils.cdf import compute_cdf_steps
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import CdfSpec

#: The number of bins used to approximate the CDF when
#: ``spec.nbins`` is ``None``. bokeh/altair/xy have no built-in
#: cumulative-step histogram (unlike matplotlib's ``Axes.hist``, see
#: ``plotmux.backends.matplotlib.cdf.render_cdf``), so a concrete bin
#: count is always needed to call ``compute_cdf_steps``.
_DEFAULT_NBINS = 100


def render_cdf(fig: figure, spec: CdfSpec, **kwargs: Any) -> figure:
    r"""Render a ``CdfSpec`` onto a bokeh ``figure``.

    bokeh has no built-in cumulative-step histogram, so the step
    curve's vertices are computed with
    ``plotmux.utils.cdf.compute_cdf_steps`` and drawn as a plain
    ``figure.line`` -- same approach as
    ``plotmux.backends.bokeh.histogram.render_histogram`` computing
    bin counts by hand with ``numpy.histogram``.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The CDF spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.line``.

    Returns:
        The ``figure`` the CDF was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    x, y = compute_cdf_steps(
        spec.values, bins=spec.nbins or _DEFAULT_NBINS, xmin=xmin, xmax=xmax
    )
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``CdfSpec.__post_init__``.
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
    fig.line(x=x, y=y, line_color=color, **kwargs)
    # Assigned as a fresh ``Range1d`` rather than mutating
    # ``fig.y_range.start``/``.end`` in place: bokeh's default ``y_range``
    # is a plain ``DataRange1d`` (auto-fit to the data), and ``Range``
    # (the common base type ``fig.y_range`` is statically typed as) declares
    # neither attribute -- only concrete subclasses like ``Range1d`` do.
    fig.y_range = Range1d(start=0, end=1)
    return fig
