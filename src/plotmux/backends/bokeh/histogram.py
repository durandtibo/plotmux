r"""Render a ``HistogramSpec`` onto a bokeh ``figure``."""

from __future__ import annotations

__all__ = ["render_histogram"]

from typing import TYPE_CHECKING, Any, cast

import numpy as np

from plotmux.backends.bokeh.style import ALPHA, LABEL, apply_fields, rgba_to_bokeh
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from bokeh.plotting import figure

    from plotmux.specs import HistogramSpec


def render_histogram(fig: figure, spec: HistogramSpec, **kwargs: Any) -> figure:
    r"""Render a ``HistogramSpec`` onto a bokeh ``figure``.

    bokeh has no built-in histogram computation (unlike matplotlib's
    ``Axes.hist``), so the bin counts and edges are computed with
    ``numpy.histogram`` and drawn as a ``figure.quad`` glyph, one
    rectangle per bin.

    Args:
        fig: The bokeh ``figure`` to draw onto.
        spec: The histogram spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``figure.quad``.

    Returns:
        The ``figure`` the histogram was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    # Cast to ``float64``: ``np.histogram`` returns an integer-dtype array of
    # counts when ``density=False``, which bokeh's ``NumberArg`` stub does not
    # accept, unlike matplotlib's ``Axes.hist``.
    counts, edges = np.histogram(
        spec.values, bins=spec.bins, range=(xmin, xmax), density=spec.density
    )
    counts = counts.astype(np.float64)
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``HistogramSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.color))
    )
    # ``LABEL``/``ALPHA`` (see ``plotmux.backends.bokeh.style``): bokeh
    # raises ``ValueError`` on ``legend_label=None`` and rejects
    # ``alpha=None`` outright, so both are only added when explicitly set.
    apply_fields(spec, [LABEL, ALPHA], kwargs)
    fig.quad(
        top=counts,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        fill_color=color,
        **kwargs,
    )
    return fig
