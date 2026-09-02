r"""Apply the common figure-level style fields onto an altair ``Chart``.

This module is only imported when altair is installed (see
``plotmux.backends.altair.__init__``), so it can import altair
unconditionally.
"""

from __future__ import annotations

__all__ = [
    "STROKE_DASH",
    "apply_common_style",
    "color_encoding",
    "prepare_color",
    "rgba_to_altair",
    "with_label_field",
]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

if TYPE_CHECKING:
    from plotmux.specs import BaseSpec

#: Maps a ``linestyle``'s matplotlib-style dash name (``LineSpec.linestyle``/
#: ``SlopeSpec.linestyle``) to the explicit on/off pixel-length list
#: altair's ``strokeDash`` expects. ``"solid"`` is deliberately absent: an
#: empty/absent ``strokeDash`` is altair's own default, a solid line. Shared
#: by ``plotmux.backends.altair.line`` and ``plotmux.backends.altair.slope``.
STROKE_DASH = {"dashed": [6, 4], "dotted": [1, 3], "dashdot": [6, 4, 1, 4]}


def rgba_to_altair(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to altair's native color string.

    altair's mark ``color`` parameter accepts a CSS color string (e.g.
    ``"rgba(255, 0, 0, 1)"``), so the canonical ``[0, 1]`` float RGBA
    tuple produced by ``plotmux.colors.parse_color`` is converted to
    that format here rather than in ``core/``, keeping ``core/`` free
    of any single backend's native color representation -- same
    pattern as ``plotmux.backends.xy.style.rgba_to_xy`` and
    ``plotmux.backends.bokeh.style.rgba_to_bokeh``.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a CSS ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a``
            as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.style import rgba_to_altair
        >>> rgba_to_altair((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"


def with_label_field(data: list[dict[str, Any]], label: str | None) -> list[dict[str, Any]]:
    r"""Attach a constant ``"label"`` field to every record when
    ``label`` is set.

    altair has no direct equivalent of matplotlib's/bokeh's
    ``label=``/``legend_label=`` mark argument -- a legend entry only
    appears for a *field-based* encoding channel (see
    ``color_encoding``), so a series label has to be carried as data,
    not as a mark option. Every per-type renderer in this backend
    calls this right before building its ``Chart`` so the resulting
    records carry a ``"label"`` field for ``color_encoding`` to bind
    to.

    Args:
        data: The records (one per data point/bin) to plot.
        label: The series label, or ``None`` for no legend entry.

    Returns:
        ``data`` unchanged if ``label`` is ``None``, otherwise a new
            list of records each with a ``"label": label`` entry
            added.
    """
    if label is None:
        return data
    return [{**row, "label": label} for row in data]


def color_encoding(color: str | None, label: str | None) -> alt.Color | None:
    r"""Build the ``color`` encoding channel for a labeled mark.

    Returns ``None`` when ``label`` is ``None``: an explicit
    ``color`` with no ``label`` is passed straight to the mark
    constructor instead (e.g. ``mark_line(color=...)``), which needs
    no encoding channel and adds no legend -- matching every other
    backend's "no label -> no legend" behavior.

    When ``label`` is set, a legend entry is only possible through a
    field-based encoding channel (see ``with_label_field``), so this
    binds ``color`` to that constant ``"label"`` field, fixing its
    displayed color to ``color`` (or altair's own default when
    ``color`` is ``None``) via an explicit ``Scale.range`` and hiding
    the (redundant, always ``"label"``-titled) legend title.

    Args:
        color: The mark's CSS color string (already converted by
            ``rgba_to_altair``), or ``None`` for the backend default.
        label: The series label, or ``None`` for no legend entry.

    Returns:
        The ``color`` encoding to pass to ``Chart.encode``, or
            ``None`` if no legend entry is needed.
    """
    if label is None:
        return None
    scale = alt.Scale(range=[color]) if color is not None else alt.Undefined
    return alt.Color("label:N", scale=scale, legend=alt.Legend(title=None))


def prepare_color(
    data: list[dict[str, Any]], label: str | None, color: str | None, kwargs: dict[str, Any]
) -> tuple[list[dict[str, Any]], alt.Color | None]:
    r"""Resolve how a mark's color and legend label should be applied.

    Every per-type renderer in this backend needs the same
    label-dependent choice: no label means the color (if any) is
    passed straight to the mark constructor and no legend entry is
    added; a label means the mark needs a field-based ``color``
    encoding instead (see ``with_label_field``/``color_encoding``),
    since that is the only way altair shows a legend. Factored here
    once so ``render_histogram``/``render_line``/``render_scatter``
    each only call this instead of repeating the branch.

    Args:
        data: The records (one per data point/bin) to plot.
        label: The series label, or ``None`` for no legend entry.
        color: The mark's CSS color string (already converted by
            ``rgba_to_altair``), or ``None`` for the backend default.
        kwargs: The caller's mark keyword arguments; mutated in place
            with a ``color`` default when ``label`` is ``None`` and
            ``color`` is set.

    Returns:
        A ``(data, color_encoding)`` pair: ``data`` with a ``"label"``
            field added when ``label`` is set (unchanged otherwise),
            and the ``color`` encoding channel to pass to
            ``Chart.encode`` (``None`` if no legend entry is needed).
    """
    if label is None:
        if color is not None:
            kwargs.setdefault("color", color)
        return data, None
    return with_label_field(data, label), color_encoding(color, label)


def apply_common_style(chart: alt.typing.ChartType, spec: BaseSpec) -> alt.typing.ChartType:
    r"""Apply the common figure-level style fields onto an altair
    ``Chart``.

    Applies ``title``/``xlabel``/``ylabel``/``xscale``/``yscale`` from
    ``spec`` (defined on ``BaseSpec``, shared by every chart type).
    Called once per backend, right after the chart-specific renderer
    has built its mark, so a new chart type gets title/label/scale
    support for free.

    Every per-type renderer in this backend (``render_histogram``/
    ``render_line``/``render_scatter``) encodes its quantitative
    channels under the fixed field names ``"x"``/``"y"`` (see each
    renderer's own docstring), so this can re-``encode`` those two
    channels -- with a title and a ``Scale`` -- generically, without
    knowing which chart type built ``chart``. Vega-Lite's shared
    top-level encoding on a layered spec (``alt.Chart.encode`` also
    works on the ``LayerChart`` produced by ``render_layer``'s ``+``)
    is what lets one call here style every child of a ``LayerSpec`` at
    once, mirroring how xy's ``apply_common_style`` appends one shared
    ``x_axis``/``y_axis`` pair after combining marks (see
    ``plotmux.backends.xy.style.apply_common_style``) instead of
    restyling each child individually.

    ``title``/``xlabel``/``ylabel`` are passed to ``alt.X``/``alt.Y``
    even when ``None`` (rather than omitted) so Vega-Lite explicitly
    hides the axis title; omitting the argument entirely would instead
    fall back to Vega-Lite's own default of showing the capitalized
    field name (``"X"``/``"Y"``), which would not match every other
    backend's "no label set -> no title shown" behavior.

    Args:
        chart: The altair ``Chart`` (or ``LayerChart``) to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The styled chart.
    """
    # ``alt.Scale``'s ``domainMin``/``domainMax`` use altair's own
    # ``alt.Undefined`` sentinel for "unset" (not ``None``, which altair
    # instead serializes as an explicit ``null`` bound), so ``spec.ymin``/
    # ``spec.ymax`` are only passed through when actually set.
    y_scale_kwargs: dict[str, Any] = {"type": spec.yscale}
    if spec.ymin is not None:
        y_scale_kwargs["domainMin"] = spec.ymin
    if spec.ymax is not None:
        y_scale_kwargs["domainMax"] = spec.ymax
    chart = chart.encode(
        x=alt.X("x:Q", title=spec.xlabel, scale=alt.Scale(type=spec.xscale)),
        y=alt.Y("y:Q", title=spec.ylabel, scale=alt.Scale(**y_scale_kwargs)),
    )
    if spec.title is not None:
        chart = chart.properties(title=spec.title)
    if spec.background_color is not None:
        # ``spec.background_color``, once set, is already a canonical RGBA
        # tuple: it went through ``parse_color`` in
        # ``BaseSpec._validate_base``. ``Chart.properties(background=...)``
        # sets the whole chart's (not just the plot area's) background,
        # matching bokeh's ``background_fill_color``/matplotlib's
        # ``Axes.set_facecolor`` closely enough for this figure-level field.
        chart = chart.properties(
            background=rgba_to_altair(
                cast("tuple[float, float, float, float]", spec.background_color)
            )
        )
    return chart
