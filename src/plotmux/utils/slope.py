r"""Contain a helper to resolve the x-range a ``SlopeSpec`` should span
when drawn by a backend with no native "line by slope, independent of
data range" primitive.
"""

from __future__ import annotations

__all__ = ["resolve_slope_xrange"]

from typing import TYPE_CHECKING

import numpy as np

from plotmux.specs import SlopeSpec
from plotmux.utils.range import find_range

if TYPE_CHECKING:
    from collections.abc import Sequence

    from plotmux.specs import BaseSpec


def resolve_slope_xrange(siblings: Sequence[BaseSpec]) -> tuple[float, float] | None:
    r"""Compute the x-range spanned by a ``SlopeSpec``'s sibling specs in
    a ``LayerSpec``.

    Unlike matplotlib's ``Axes.axline``/bokeh's ``bokeh.models.Slope``
    (see ``plotmux.backends.matplotlib.slope``/
    ``plotmux.backends.bokeh.slope``), altair and xy have no native
    primitive for a line defined by slope alone, spanning whatever the
    current view happens to be -- both need two concrete ``(x, y)``
    endpoints instead (see
    ``plotmux.backends.altair.slope.render_slope``/
    ``plotmux.backends.xy.slope.render_slope``). This is what makes a
    standalone ``SlopeSpec`` unsupported on those two backends (see
    DESIGN.md, section 8.1): there is no data to derive endpoints
    from. Inside a ``LayerSpec``, though, the other, data-bound
    children (a ``LineSpec``/``ScatterSpec``/``BarSpec``'s own ``x``,
    or a ``HistogramSpec``/``CdfSpec``'s resolved x-range) supply that
    range, so ``render_layer`` calls this once per ``SlopeSpec`` child
    to compute it.

    Args:
        siblings: Every child spec in the same ``LayerSpec`` as the
            ``SlopeSpec`` being resolved (including that ``SlopeSpec``
            itself and any other ``SlopeSpec`` siblings -- both are
            skipped, since neither owns any data of its own to
            contribute a range).

    Returns:
        The ``(min, max)`` x-range spanned by every data-bound
            sibling, or ``None`` if ``siblings`` has no data-bound
            spec to derive a range from (e.g. a layer made up only of
            ``SlopeSpec`` children).
    """
    los: list[float] = []
    his: list[float] = []
    for sibling in siblings:
        if isinstance(sibling, SlopeSpec):
            continue
        x = getattr(sibling, "x", None)
        if x is not None:
            los.append(float(np.min(x)))
            his.append(float(np.max(x)))
            continue
        values = getattr(sibling, "values", None)
        if values is not None:
            xmin, xmax = find_range(
                np.asarray(values),
                xmin=getattr(sibling, "xmin", None),
                xmax=getattr(sibling, "xmax", None),
            )
            los.append(xmin)
            his.append(xmax)
    if not los:
        return None
    return min(los), max(his)
