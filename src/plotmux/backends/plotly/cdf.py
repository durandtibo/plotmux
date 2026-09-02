r"""Render a ``CdfSpec`` onto a plotly ``Figure``."""

from __future__ import annotations

__all__ = ["render_cdf"]

from typing import TYPE_CHECKING, Any, cast

import plotly.graph_objects as go

from plotmux.backends.plotly.style import rgba_to_plotly
from plotmux.utils.cdf import compute_cdf_steps
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from plotmux.specs import CdfSpec

#: The number of bins used to approximate the CDF when ``spec.nbins``
#: is ``None``. plotly has no built-in cumulative-step histogram
#: (unlike matplotlib's ``Axes.hist``), so a concrete bin count is
#: always needed to call ``compute_cdf_steps`` -- same constant as
#: ``plotmux.backends.bokeh.cdf._DEFAULT_NBINS``.
_DEFAULT_NBINS = 100


def render_cdf(
    fig: Figure, spec: CdfSpec, *, row: int | None = None, col: int | None = None, **kwargs: Any
) -> Figure:
    r"""Render a ``CdfSpec`` onto a plotly ``Figure``.

    The step curve's vertices are computed with
    ``plotmux.utils.cdf.compute_cdf_steps`` and drawn as a plain
    ``go.Scatter`` line -- same approach as
    ``plotmux.backends.bokeh.cdf.render_cdf``.

    Args:
        fig: The plotly ``Figure`` to draw onto.
        spec: The CDF spec to render.
        row: The 1-indexed subplot row to draw onto (see
            ``plotmux.backends.plotly.histogram.render_histogram``).
        col: The 1-indexed subplot column to draw onto.
        **kwargs: Additional keyword arguments forwarded to
            ``go.Scatter``.

    Returns:
        The ``Figure`` the CDF was drawn onto.
    """
    xmin, xmax = find_range(spec.values, xmin=spec.xmin, xmax=spec.xmax)
    x, y = compute_cdf_steps(spec.values, bins=spec.nbins or _DEFAULT_NBINS, xmin=xmin, xmax=xmax)
    # ``spec.color``, once set, is already a canonical RGBA tuple: it went
    # through ``parse_color`` in ``CdfSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_plotly(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.label is not None:
        kwargs.setdefault("name", spec.label)
        kwargs.setdefault("showlegend", True)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    line: dict[str, Any] = {}
    if color is not None:
        line["color"] = color
    kwargs.setdefault("line", line)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", **kwargs), row=row, col=col)
    fig.update_yaxes(range=[0, 1], row=row, col=col)
    return fig
