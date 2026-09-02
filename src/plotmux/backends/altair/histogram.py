r"""Render a ``HistogramSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt
import numpy as np

from plotmux.backends.altair.style import prepare_color, rgba_to_altair
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from plotmux.specs import HistogramSpec


def render_histogram(spec: HistogramSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``HistogramSpec`` into an altair ``Chart``.

    altair has no built-in histogram computation (unlike Vega-Lite's
    declarative ``bin`` transform, which cannot express an explicit
    ``range``/quantile-resolved bound the way ``find_range`` does), so
    bin counts and edges are computed with ``numpy.histogram`` and
    drawn as a ``mark_bar`` with explicit ``x``/``x2`` bin edges --
    same approach as
    ``plotmux.backends.bokeh.histogram.render_histogram``'s
    ``figure.quad``.

    The quantitative channels are encoded under the field names
    ``"x"`` (bin left edge) and ``"y"`` (count), the fixed convention
    every renderer in this backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact; the bin right edge is carried
    under a third field, ``"x2"``, which ``apply_common_style`` never
    touches.

    Args:
        spec: The histogram spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_bar``.

    Returns:
        The resulting altair ``Chart``.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    counts, edges = np.histogram(
        spec.values, bins=spec.bins, range=(xmin, xmax), density=spec.density
    )
    data = [
        {"x": left, "x2": right, "y": count}
        for left, right, count in zip(edges[:-1], edges[1:], counts)
    ]
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``HistogramSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    chart = alt.Chart(alt.Data(values=data)).mark_bar(**kwargs).encode(x="x:Q", x2="x2:Q", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
