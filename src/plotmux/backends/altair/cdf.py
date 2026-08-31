r"""Render a ``CdfSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_cdf"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import prepare_color, rgba_to_altair
from plotmux.utils.cdf import compute_cdf_steps
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from plotmux.specs import CdfSpec

#: The number of bins used to approximate the CDF when
#: ``spec.nbins`` is ``None``. Mirrors
#: ``plotmux.backends.bokeh.cdf._DEFAULT_NBINS``.
_DEFAULT_NBINS = 100


def render_cdf(spec: CdfSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``CdfSpec`` into an altair ``Chart``.

    altair has no built-in cumulative-step histogram, so the step
    curve's vertices are computed with
    ``plotmux.utils.cdf.compute_cdf_steps`` and drawn as a plain
    ``mark_line`` -- same approach as
    ``plotmux.backends.altair.histogram.render_histogram`` computing
    bin counts by hand with ``numpy.histogram``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    Args:
        spec: The CDF spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_line``.

    Returns:
        The resulting altair ``Chart``.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    x, y = compute_cdf_steps(spec.values, bins=spec.nbins or _DEFAULT_NBINS, xmin=xmin, xmax=xmax)
    data = [{"x": xi, "y": yi} for xi, yi in zip(x, y)]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``CdfSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    chart = alt.Chart(alt.Data(values=data)).mark_line(**kwargs).encode(x="x:Q", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
