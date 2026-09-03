r"""Contain xy-specific style helpers shared across chart types.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["apply_common_style", "rgba_to_xy"]

from typing import TYPE_CHECKING, cast

import xy

if TYPE_CHECKING:
    from plotmux.specs import BaseSpec


def rgba_to_xy(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to xy's native CSS color string.

    xy's mark color parameters accept a CSS color string (e.g.
    ``"rgba(255, 0, 0, 1)"``), so the canonical ``[0, 1]`` float RGBA
    tuple produced by ``plotmux.colors.parse_color`` is converted
    to that format here rather than in ``core/``, keeping ``core/``
    free of any single backend's native color representation.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a CSS ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a``
            as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.xy.style import rgba_to_xy
        >>> rgba_to_xy((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"


def apply_common_style(chart: xy.Chart, spec: BaseSpec) -> xy.Chart:
    r"""Apply the common figure-level style fields onto an xy ``Chart``.

    Applies ``title``/``xlabel``/``ylabel``/``xscale``/``yscale``/
    ``ymin``/``ymax``/``xmin``/``xmax``/``legend_title``/
    ``legend_location`` from ``spec`` (defined on ``BaseSpec``, shared
    by every chart type). Called once per backend, right after the
    chart-specific renderer has built its ``Chart``, so a new chart
    type gets title/label/scale support for free.

    ``legend_title``/``legend_location`` are appended as one
    ``xy.legend(title=..., loc=...)`` chrome child alongside the
    ``x_axis``/``y_axis`` pair below, mirroring bokeh's
    ``fig.legend.title``/``.location``/altair's legend-only ``color``
    re-``encode`` -- unlike those two, xy's ``legend`` chrome needs no
    "does a legend already exist" guard: an ``xy.legend()`` with no
    named series simply draws nothing, so it is safe to append
    unconditionally whenever either is set.

    xy charts are structure-immutable (see ``xy.Chart.append``'s
    docstring), so this builds a new ``Chart`` instead of mutating
    ``chart`` in place: the existing children (the mark(s) already
    drawn) are kept and an ``x_axis``/``y_axis`` pair carrying
    ``xlabel``/``ylabel`` and ``xscale``/``yscale`` is appended.
    Layout (``width``/``height``/``padding``/``data``) is copied over
    unchanged from ``chart``; other constructor arguments (styling,
    interaction, linking, ...) are intentionally not reflected off
    ``chart`` here -- several (e.g. ``select``) are stored under a
    private attribute name specifically because the public name
    collides with a same-named ``Chart`` method, so generic
    ``getattr`` introspection over ``xy.Chart``'s signature would
    silently pick up the wrong (bound-method) value.

    Args:
        chart: The xy ``Chart`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        A new ``Chart`` with the common style fields applied.
    """
    # ``xy.y_axis``'s ``domain`` takes both bounds together (``tuple[float,
    # float]``, no partial-bound form) -- unlike matplotlib's
    # ``Axes.set_ylim``/bokeh's ``y_range.start``/``.end`` (see
    # ``plotmux.backends.matplotlib.style``/
    # ``plotmux.backends.bokeh.style``), which can pin just one bound and
    # leave the other autoscaled. So only both explicit bounds together are
    # forwarded here; either alone is left for xy's own autoscale, same as
    # neither being set.
    y_domain = (spec.ymin, spec.ymax) if spec.ymin is not None and spec.ymax is not None else None
    # Same "both bounds together, or neither" shape as ``y_domain`` above,
    # for the x-axis.
    x_domain = (spec.xmin, spec.xmax) if spec.xmin is not None and spec.xmax is not None else None
    children = (
        *chart.children,
        xy.x_axis(label=spec.xlabel, type_=spec.xscale, domain=x_domain),
        xy.y_axis(label=spec.ylabel, type_=spec.yscale, domain=y_domain),
    )
    if spec.legend_title is not None or spec.legend_location is not None:
        # ``BaseSpec.legend_location``'s portable names (``"top_left"``,
        # ...) match xy's own ``legend(loc=...)`` vocabulary once
        # underscore-tokenized (xy accepts both `"_"` and `" "` as token
        # separators, see ``xy._validate.legend_loc``), including
        # ``"best"`` (xy's own auto-placement mode) -- so, unlike every
        # other backend, this needs no translation table at all.
        children = (
            *children,
            xy.legend(title=spec.legend_title, loc=spec.legend_location),
        )
    style = dict(chart.style or {})
    if spec.background_color is not None:
        # ``spec.background_color``, once set, is already a canonical RGBA
        # tuple: it went through ``parse_color`` in
        # ``BaseSpec._validate_base``.
        style["backgroundColor"] = rgba_to_xy(
            cast("tuple[float, float, float, float]", spec.background_color)
        )
    return xy.Chart(
        chart.kind,
        children,
        title=spec.title,
        width=chart.width,
        height=chart.height,
        padding=chart.padding,
        data=chart.data,
        style=style or None,
    )
