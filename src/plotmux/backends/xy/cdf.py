r"""Render a ``CdfSpec`` into an xy ``Chart``."""

from __future__ import annotations

__all__ = ["render_cdf"]

from typing import TYPE_CHECKING, Any, cast

import xy

from plotmux.backends.xy.style import rgba_to_xy
from plotmux.utils.cdf import compute_cdf_steps
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from plotmux.specs import CdfSpec

#: The number of bins used to approximate the CDF when
#: ``spec.nbins`` is ``None``. Mirrors
#: ``plotmux.backends.bokeh.cdf._DEFAULT_NBINS``.
_DEFAULT_NBINS = 100


def render_cdf(spec: CdfSpec, **kwargs: Any) -> xy.Chart:
    r"""Render a ``CdfSpec`` into an xy ``Chart``.

    xy has no built-in cumulative-step histogram, so the step curve's
    vertices are computed with ``plotmux.utils.cdf.compute_cdf_steps``
    and drawn as a plain ``xy.line`` -- same approach as
    ``plotmux.backends.xy.histogram.render_histogram`` relying on
    ``xy.hist`` for its own regular, non-cumulative form.

    Args:
        spec: The CDF spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``xy.line``.

    Returns:
        The resulting xy ``Chart``.
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
        else rgba_to_xy(cast("tuple[float, float, float, float]", spec.color))
    )
    return xy.line_chart(
        xy.line(x, y, name=spec.label, color=color, **kwargs),
    )
