r"""Apply the common figure-level style fields onto a bokeh ``figure``.

This module is only imported when bokeh is installed (see
``plotmux.backends.bokeh.__init__``), so it can import bokeh
unconditionally.
"""

from __future__ import annotations

__all__ = ["apply_common_style", "rgba_to_bokeh"]

from typing import TYPE_CHECKING, cast

from bokeh.colors import RGB

from plotmux.specs import XBoundSpec

if TYPE_CHECKING:
    from bokeh.models import DataRange1d
    from bokeh.plotting import figure

    from plotmux.specs import BaseSpec

#: ``BaseSpec.legend_location``'s portable position names were chosen to
#: match bokeh's own ``fig.legend.location`` vocabulary directly (e.g.
#: ``"top_left"``), so no translation table is needed here -- unlike
#: matplotlib's (see
#: ``plotmux.backends.matplotlib.style.LEGEND_LOCATION``). ``"top"``/
#: ``"bottom"``/``"left"``/``"right"`` also match bokeh's own vocabulary
#: as-is.


def rgba_to_bokeh(color: tuple[float, float, float, float]) -> RGB:
    r"""Convert a canonical RGBA tuple to bokeh's native color type.

    bokeh's glyph color parameters (e.g. ``line_color``, ``fill_color``)
    accept a ``bokeh.colors.RGB`` instance, so the canonical ``[0, 1]``
    float RGBA tuple produced by ``plotmux.colors.parse_color`` is
    converted to that format here rather than in ``core/``, keeping
    ``core/`` free of any single backend's native color representation
    -- same pattern as ``plotmux.backends.xy.style.rgba_to_xy``.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a ``bokeh.colors.RGB``, with ``r``/``g``/``b`` as
            integers in ``[0, 255]`` and ``a`` as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.bokeh.style import rgba_to_bokeh
        >>> rgba_to_bokeh((1.0, 0.0, 0.0, 1.0))
        rgb(255, 0, 0)

        ```
    """
    r, g, b, a = color
    return RGB(round(r * 255), round(g * 255), round(b * 255), a)


def _apply_xbounds(fig: figure, spec: BaseSpec) -> None:
    r"""Pin ``fig.x_range``'s ``start``/``end`` from ``spec.xmin``/
    ``.xmax``, for every spec type that carries a plain, explicit-value-
    only x-axis bound.

    Split out of ``apply_common_style`` so that function's own branch
    count stays under the linter's limit; also keeps the ``XBoundSpec``
    gate (see ``plotmux.specs.base.XBoundSpec``) -- ``HistogramSpec``/
    ``CdfSpec`` are not ``XBoundSpec``, since their own ``xmin``/``xmax``
    may hold an unresolved quantile string, resolved and applied by
    their own renderer instead.

    Args:
        fig: The bokeh ``figure`` whose ``x_range`` to pin.
        spec: The spec whose ``xmin``/``xmax`` to apply, if any.
    """
    if not isinstance(spec, XBoundSpec):
        return
    # Same shape as ``y_range`` in ``apply_common_style``, for the x-axis.
    x_range = cast("DataRange1d", fig.x_range)
    if spec.xmin is not None:
        x_range.start = spec.xmin
    if spec.xmax is not None:
        x_range.end = spec.xmax


def apply_common_style(fig: figure, spec: BaseSpec) -> figure:
    r"""Apply the common figure-level style fields onto a bokeh
    ``figure``.

    Applies ``title``/``xlabel``/``ylabel``/``ymin``/``ymax``/
    ``xmin``/``xmax``/``legend_title``/``legend_location``/
    ``legend_orientation`` from
    ``spec`` (defined on ``BaseSpec``, shared by every chart type).
    Called once per backend, right after the chart-specific renderer
    has drawn its glyph, so a new chart type gets title/label support
    for free.

    Unlike matplotlib's ``Axes.set_xscale``, bokeh's axis type
    (``"linear"``/``"log"``) is a construction-time argument of
    ``bokeh.plotting.figure`` (``x_axis_type``/``y_axis_type``), not a
    mutable property that can be flipped after glyphs are added -- so
    ``spec.xscale``/``spec.yscale`` are applied where the figure is
    created (``backends/bokeh/backend.py::_make_renderer``), not here.

    Args:
        fig: The bokeh ``figure`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The ``figure`` that was styled.
    """
    if spec.title is not None:
        fig.title = spec.title
    if spec.xlabel is not None:
        fig.xaxis.axis_label = spec.xlabel
    if spec.ylabel is not None:
        fig.yaxis.axis_label = spec.ylabel
    if spec.background_color is not None:
        # ``spec.background_color``, once set, is already a canonical RGBA
        # tuple: it went through ``parse_color`` in
        # ``BaseSpec._validate_base``. ``figure.background_fill_color`` is
        # statically typed as bokeh's ``Color`` union, which does not
        # include ``bokeh.colors.RGB`` even though it is accepted at
        # runtime -- same pre-existing gap as every glyph's ``fill_color``/
        # ``line_color`` elsewhere in this backend (e.g.
        # ``plotmux.backends.bokeh.scatter.render_scatter``).
        fig.background_fill_color = cast(
            "str",
            rgba_to_bokeh(cast("tuple[float, float, float, float]", spec.background_color)),
        )
    # bokeh's default ``y_range`` is a ``DataRange1d`` (auto-fit to the
    # data), whose ``start``/``end`` can still be pinned individually
    # without losing auto-fit on the bound left unset -- unlike
    # ``plotmux.backends.bokeh.cdf.render_cdf``, which replaces the whole
    # range with a ``Range1d`` because it always pins both bounds at once.
    # ``figure.y_range`` is statically typed as the abstract ``Range`` base
    # class, which declares neither attribute (only concrete subclasses
    # like ``DataRange1d`` do, see ``render_cdf``'s own such comment), so
    # it is cast to narrow it for the assignment.
    y_range = cast("DataRange1d", fig.y_range)
    if spec.ymin is not None:
        y_range.start = spec.ymin
    if spec.ymax is not None:
        y_range.end = spec.ymax
    # Same shape as ``y_range`` above, for the x-axis. Factored into its own
    # function (rather than inlined like ``y_range`` above) so this
    # function's own branch count stays under the linter's limit -- gated on
    # ``XBoundSpec``: ``HistogramSpec``/``CdfSpec`` are not ``XBoundSpec``
    # (their own ``xmin``/``xmax`` accept a quantile string, resolved and
    # applied by their own renderer -- see ``plotmux.specs.base.XBoundSpec``).
    _apply_xbounds(fig, spec)
    # bokeh auto-creates ``fig.legend`` once any glyph carries a
    # ``legend_label``; setting ``fig.legend.title``/``.location`` when none
    # exists prints a "zero legends added" warning, so both are only set
    # when a legend actually exists (``fig.legend`` is an empty splattable
    # list otherwise, falsy) -- same shape of guard as bokeh's own
    # ``alpha``/``linewidth`` "only set when explicitly given" pattern
    # elsewhere in this backend.
    if fig.legend:
        if spec.legend_title is not None:
            fig.legend.title = spec.legend_title
        # bokeh has no "best" auto-placement location (unlike matplotlib's
        # ``loc="best"``, see
        # ``plotmux.backends.matplotlib.style.apply_common_style``); every
        # other portable name matches bokeh's own vocabulary directly, so
        # only ``"best"`` is excluded here, falling back to bokeh's own
        # default position, same as ``legend_location`` unset.
        if spec.legend_location is not None and spec.legend_location != "best":
            fig.legend.location = spec.legend_location
        if spec.legend_orientation is not None:
            # bokeh's own vocabulary, matched one-to-one.
            fig.legend.orientation = spec.legend_orientation
    return fig
