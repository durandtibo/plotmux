r"""Contain the public plotting API.

Every function builds the spec of a mark, wraps it in a ``PanelSpec``
and renders it. The axes options are the same for every chart, they are
declared once in ``PanelOptions`` and ``BoundedPanelOptions``.
"""

from __future__ import annotations

__all__ = [
    "BoundedPanelOptions",
    "PanelOptions",
    "bar",
    "cdf",
    "grid",
    "hist",
    "layer",
    "line",
    "scatter",
    "slope",
    "stacked_bar",
]

from dataclasses import fields
from typing import TYPE_CHECKING, Any, Literal, TypedDict, Unpack

import numpy as np

from plotmux.backends.registry import get_backend
from plotmux.config import get_default_backend
from plotmux.exceptions import InvalidSpecError
from plotmux.figure import Figure
from plotmux.specs import (
    BarSeries,
    BarSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    MarkSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from plotmux.colors import Color
    from plotmux.specs import LegendLocation


class PanelOptions(TypedDict, total=False):
    r"""Define the axes options of every plotting function.

    These keyword arguments are accepted by every plotting function
    (``hist``, ``line``, ...), and have the meaning of the fields of
    ``plotmux.specs.PanelSpec``. A misspelled keyword is a
    ``TypeError`` at the call site, whatever the backend.

    Args:
        title: An optional axes title.
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
        ymin: An optional explicit lower limit of the y-axis.
            ``None`` leaves the axis autoscaled.
        ymax: An optional explicit upper limit of the y-axis.
        background_color: An optional axes background color. Same
            format as the ``color`` of a mark. ``None`` uses the
            backend's default.
        legend_title: An optional heading of the legend box.
        legend_location: An optional legend position, one of
            ``"top_left"``, ``"top_right"``, ``"bottom_left"``,
            ``"bottom_right"``, ``"top"``, ``"bottom"``, ``"left"``
            or ``"right"``. ``None`` uses the backend's default.
        legend_orientation: An optional legend layout,
            ``"vertical"`` or ``"horizontal"``.
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
    """

    title: str | None
    xlabel: str | None
    ylabel: str | None
    xscale: Literal["linear", "log"]
    yscale: Literal["linear", "log"]
    ymin: float | None
    ymax: float | None
    background_color: Color
    legend_title: str | None
    legend_location: LegendLocation | None
    legend_orientation: Literal["vertical", "horizontal"] | None
    backend: str | None


class BoundedPanelOptions(PanelOptions, total=False):
    r"""Define the axes options of the charts that have an x-axis limit.

    It adds the limits of the x-axis to ``PanelOptions``. ``hist`` and
    ``cdf`` do not take them: their ``xmin``/``xmax`` are the range of
    the data they bin or plot.

    Args:
        xmin: An optional explicit lower limit of the x-axis.
            ``None`` leaves the axis autoscaled.
        xmax: An optional explicit upper limit of the x-axis.
    """

    xmin: float | None
    xmax: float | None


_PANEL_KEYS = PanelOptions.__optional_keys__
_BOUNDED_PANEL_KEYS = BoundedPanelOptions.__optional_keys__


def _check_options(function: str, options: Mapping[str, Any], allowed: frozenset[str]) -> None:
    r"""Check that the keyword options of a plotting function are known.

    The axes options are collected by ``**panel`` and forwarded to
    ``PanelSpec``, so an unknown keyword is checked here to be a
    ``TypeError`` of the function the user called, with the valid names.

    Args:
        function: The name of the plotting function, used in the message.
        options: The keyword options collected by ``**panel``.
        allowed: The names of the axes options of the function.

    Raises:
        TypeError: if ``options`` has a key that is not in ``allowed``.

    Example:
        ```pycon
        >>> from plotmux.api import _check_options
        >>> _check_options("hist", {"title": "t"}, frozenset({"title"}))

        ```
    """
    for key in options:
        if key not in allowed:
            msg = (
                f"{function}() got an unexpected keyword argument {key!r}. "
                f"The axes options are: {', '.join(sorted(allowed))}"
            )
            raise TypeError(msg)


def _render(spec: PanelSpec | GridSpec, backend: str | None) -> Figure:
    r"""Render a spec through a backend and wrap the result in a
    ``Figure``.

    Args:
        spec: The spec to render.
        backend: The name of the backend to use, or ``None`` to use
            the current default backend (see
            ``plotmux.config.get_default_backend``).

    Returns:
        The rendered figure.
    """
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec)
    return Figure(spec=spec, backend_name=backend_name, native=native)


def _render_mark(mark: MarkSpec, options: Mapping[str, Any]) -> Figure:
    r"""Wrap one mark in a panel and render it.

    Args:
        mark: The mark to draw.
        options: The axes options of the call, with the ``backend``.

    Returns:
        The rendered figure.
    """
    return _render_marks((mark,), options)


def _render_marks(marks: tuple[MarkSpec, ...], options: Mapping[str, Any]) -> Figure:
    r"""Wrap marks in a panel and render it.

    Args:
        marks: The marks to draw.
        options: The axes options of the call, with the ``backend``.

    Returns:
        The rendered figure.
    """
    axes = dict(options)
    backend = axes.pop("backend", None)
    return _render(PanelSpec(marks=marks, **axes), backend)


def hist(
    values: Sequence[float] | np.ndarray,
    *,
    bins: int = 30,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    density: bool = False,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    **panel: Unpack[PanelOptions],
) -> Figure:
    r"""Plot a histogram.

    Args:
        values: The array of values to plot.
        bins: The number of histogram bins. Must be a positive
            integer.
        xmin: Specifies the lower bound of the range of the values
            that are binned. It can be an explicit value, a quantile
            string such as ``"q0.1"``, or ``None`` to use the minimum
            of ``values``. It is not an axis limit.
        xmax: Specifies the upper bound of the range of the values
            that are binned. Same semantics as ``xmin``.
        density: If ``True``, draw a probability density: each bin
            displays the bin's raw count divided by the total number
            of counts and the bin width, so that the area under the
            histogram integrates to 1.
        label: An optional label used in the legend.
        color: An optional color for the bars. It can be a hex string
            (``"#rrggbb"`` or ``"#rrggbbaa"``), a CSS/matplotlib named
            color (e.g. ``"tab:blue"``), or an RGB(A) tuple of floats
            in ``[0, 1]``. ``None`` takes the next color of the
            default palette.
        alpha: An optional bar opacity, in ``[0, 1]``.
        **panel: The axes options, see ``PanelOptions``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.hist([1, 2, 2, 3], bins=3, backend="matplotlib")

        ```
    """
    _check_options("hist", panel, _PANEL_KEYS)
    mark = HistogramSpec(
        values=np.asarray(values),
        bins=bins,
        xmin=xmin,
        xmax=xmax,
        density=density,
        label=label,
        color=color,
        alpha=alpha,
    )
    return _render_mark(mark, panel)


def bar(
    x: Sequence[float] | Sequence[str] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    width: float = 0.8,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    **panel: Unpack[BoundedPanelOptions],
) -> Figure:
    r"""Plot a bar chart.

    Args:
        x: The array of bar positions: numbers, or strings for a
            categorical x-axis.
        y: The array of bar heights. Must have the same length as
            ``x``.
        width: The width of each bar, in ``x`` data units (a fraction
            of the band for a categorical ``x``). Must be positive.
        label: An optional label used in the legend.
        color: An optional color for the bars (see ``hist``).
        alpha: An optional bar opacity, in ``[0, 1]``.
        **panel: The axes options, see ``BoundedPanelOptions``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.bar(["a", "b"], [1, 2], backend="matplotlib")

        ```
    """
    _check_options("bar", panel, _BOUNDED_PANEL_KEYS)
    mark = BarSpec(
        x=np.asarray(x), y=np.asarray(y), width=width, label=label, color=color, alpha=alpha
    )
    return _render_mark(mark, panel)


def stacked_bar(
    x: Sequence[float] | Sequence[str] | np.ndarray,
    series: Sequence[BarSeries],
    *,
    width: float = 0.8,
    alpha: float | None = None,
    **panel: Unpack[BoundedPanelOptions],
) -> Figure:
    r"""Plot a stacked bar chart.

    Args:
        x: The array of bar positions, shared by every series:
            numbers, or strings for a categorical x-axis.
        series: The series to stack, bottom to top. Each series has
            its own label and color.
        width: The width of each bar, in ``x`` data units (a fraction
            of the band for a categorical ``x``). Must be positive.
        alpha: An optional bar opacity, in ``[0, 1]``, for every
            series.
        **panel: The axes options, see ``BoundedPanelOptions``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> from plotmux.specs import BarSeries
        >>> fig = plotmux.stacked_bar(
        ...     ["a", "b"], [BarSeries(y=[1, 2])], backend="matplotlib"
        ... )

        ```
    """
    _check_options("stacked_bar", panel, _BOUNDED_PANEL_KEYS)
    mark = StackedBarSpec(x=np.asarray(x), series=tuple(series), width=width, alpha=alpha)
    return _render_mark(mark, panel)


def cdf(
    values: Sequence[float] | np.ndarray,
    *,
    nbins: int | None = None,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    **panel: Unpack[PanelOptions],
) -> Figure:
    r"""Plot an empirical cumulative distribution function.

    The curve is the exact ``P(X <= x)`` over all the values.

    Args:
        values: The array of values to plot.
        nbins: ``None`` for the exact CDF, or a positive integer to
            bin the values first and bound the number of vertices for
            a large input.
        xmin: Specifies the lower bound of the part of the curve that
            is drawn. It can be an explicit value, a quantile string
            such as ``"q0.1"``, or ``None`` to use the minimum of
            ``values``. It does not renormalize the curve and is not
            an axis limit.
        xmax: Specifies the upper bound of the part of the curve that
            is drawn. Same semantics as ``xmin``.
        label: An optional label used in the legend.
        color: An optional color for the curve (see ``hist``).
        alpha: An optional curve opacity, in ``[0, 1]``.
        **panel: The axes options, see ``PanelOptions``. ``ylabel``
            defaults to ``"cumulative probability"``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.cdf([1, 2, 2, 3], backend="matplotlib")

        ```
    """
    _check_options("cdf", panel, _PANEL_KEYS)
    mark = CdfSpec(
        values=np.asarray(values),
        nbins=nbins,
        xmin=xmin,
        xmax=xmax,
        label=label,
        color=color,
        alpha=alpha,
    )
    return _render_mark(mark, {"ylabel": "cumulative probability", **panel})


def line(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    linewidth: float | None = None,
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid",
    **panel: Unpack[BoundedPanelOptions],
) -> Figure:
    r"""Plot a line chart.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as ``x``.
        label: An optional label used in the legend.
        color: An optional color for the line (see ``hist``).
        alpha: An optional line opacity, in ``[0, 1]``.
        linewidth: An optional line width.
        linestyle: The line's dash style.
        **panel: The axes options, see ``BoundedPanelOptions``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.line([1, 2, 3], [1, 4, 9], backend="matplotlib")

        ```
    """
    _check_options("line", panel, _BOUNDED_PANEL_KEYS)
    mark = LineSpec(
        x=np.asarray(x),
        y=np.asarray(y),
        label=label,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
    )
    return _render_mark(mark, panel)


def scatter(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    label: str | None = None,
    color: Color = None,
    size: float | None = None,
    edgecolor: Color = None,
    alpha: float | None = None,
    marker: Literal["circle", "square", "triangle", "diamond", "cross", "x"] | None = None,
    fill: bool | None = None,
    **panel: Unpack[BoundedPanelOptions],
) -> Figure:
    r"""Plot a scatter chart.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as ``x``.
        label: An optional label used in the legend.
        color: An optional color for the markers (see ``hist``).
        size: An optional marker size.
        edgecolor: An optional color for the marker edge.
        alpha: An optional marker opacity, in ``[0, 1]``.
        marker: An optional marker shape.
        fill: ``False`` draws hollow markers.
        **panel: The axes options, see ``BoundedPanelOptions``.

    Returns:
        The rendered figure.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.scatter([1, 2, 3], [1, 4, 9], backend="matplotlib")

        ```
    """
    _check_options("scatter", panel, _BOUNDED_PANEL_KEYS)
    mark = ScatterSpec(
        x=np.asarray(x),
        y=np.asarray(y),
        label=label,
        color=color,
        size=size,
        edgecolor=edgecolor,
        alpha=alpha,
        marker=marker,
        fill=fill,
    )
    return _render_mark(mark, panel)


def slope(
    gradient: float,
    intercept: float = 0.0,
    *,
    label: str | None = None,
    color: Color = None,
    linewidth: float | None = None,
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid",
    alpha: float | None = None,
    **panel: Unpack[BoundedPanelOptions],
) -> Figure:
    r"""Plot a line given by its slope and intercept.

    The line is drawn over the x extent of the panel: ``xmin`` and
    ``xmax`` of ``panel``, which are required here as the slope has no
    data of its own (in a ``layer``, the data of the other marks gives
    the extent).

    Args:
        gradient: The slope of the line.
        intercept: The y-intercept of the line.
        label: An optional label used in the legend.
        color: An optional color for the line (see ``hist``).
        linewidth: An optional line width.
        linestyle: The line's dash style.
        alpha: An optional line opacity, in ``[0, 1]``.
        **panel: The axes options, see ``BoundedPanelOptions``.

    Returns:
        The rendered figure.

    Raises:
        InvalidSpecError: if ``panel`` has no ``xmin`` and ``xmax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.slope(2, 1, xmin=0, xmax=10, backend="matplotlib")

        ```
    """
    _check_options("slope", panel, _BOUNDED_PANEL_KEYS)
    mark = SlopeSpec(
        gradient=gradient,
        intercept=intercept,
        label=label,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
    )
    return _render_mark(mark, panel)


def layer(*items: MarkSpec | Figure, **panel: Unpack[BoundedPanelOptions]) -> Figure:
    r"""Draw several marks on one shared axes.

    A ``Figure`` of a single panel contributes its marks and its axes
    options. A mark with no data of its own (a ``SlopeSpec``) is given
    as the mark, not as a figure: ``plotmux.slope`` alone needs
    ``xmin`` and ``xmax``. For each axes option the call does not set, the unique
    non-default value of the figures is used.

    Args:
        *items: The marks and the single-panel figures, in drawing
            order.
        **panel: The axes options, see ``BoundedPanelOptions``. They
            win over the options of the figures.

    Returns:
        The rendered figure.

    Raises:
        InvalidSpecError: if a figure is a grid, or two figures have
            different non-default values of an axes option that the
            call does not set.

    Example:
        ```pycon
        >>> import plotmux
        >>> from plotmux.specs import SlopeSpec
        >>> fig = plotmux.layer(
        ...     plotmux.line([1, 2], [1, 2]), SlopeSpec(gradient=1), backend="matplotlib"
        ... )

        ```
    """
    _check_options("layer", panel, _BOUNDED_PANEL_KEYS)
    marks: list[MarkSpec] = []
    figure_panels: list[PanelSpec] = []
    for item in items:
        if isinstance(item, MarkSpec):
            marks.append(item)
        else:
            figure_panel = _as_panel(item)
            figure_panels.append(figure_panel)
            marks.extend(figure_panel.marks)
    return _render_marks(tuple(marks), _merge_axes_options(figure_panels, panel))


def grid(
    *items: PanelSpec | MarkSpec | Figure,
    ncols: int = 1,
    title: str | None = None,
    backend: str | None = None,
) -> Figure:
    r"""Draw several panels as independent axes in a grid.

    Args:
        *items: The panels, the marks (each wrapped in a default
            panel) and the single-panel figures, in row-major order.
        ncols: The number of columns. Must be a positive integer.
        title: An optional title of the whole grid.
        backend: The name of the backend to use, or ``None`` to use
            the current default backend.

    Returns:
        The rendered figure.

    Raises:
        InvalidSpecError: if a figure is a grid.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.grid(
        ...     plotmux.hist([1, 2, 3]), plotmux.line([1, 2], [1, 2]), ncols=2, backend="matplotlib"
        ... )

        ```
    """
    spec = GridSpec(panels=tuple(_as_panel(item) for item in items), ncols=ncols, title=title)
    return _render(spec, backend)


def _as_panel(item: PanelSpec | MarkSpec | Figure) -> PanelSpec:
    r"""Convert an item of ``layer`` or ``grid`` to a panel.

    Args:
        item: A panel, a mark, or a figure of a single panel.

    Returns:
        The panel: the item itself, a default panel holding the mark,
            or the panel of the figure.

    Raises:
        InvalidSpecError: if the item is a figure of a grid. Also a
            ``ValueError``.
    """
    spec = item.spec if isinstance(item, Figure) else item
    if isinstance(spec, GridSpec):
        msg = "a grid cannot be an item of layer or grid: only a single-panel figure can"
        raise InvalidSpecError(msg)
    if isinstance(spec, PanelSpec):
        return spec
    return PanelSpec(marks=(spec,))


def _merge_axes_options(
    panels: Sequence[PanelSpec], explicit: BoundedPanelOptions
) -> dict[str, Any]:
    r"""Merge the axes options of the panels given to ``layer``.

    The explicit options win. For an option that is not explicit, the
    unique non-default value of the panels is used, and two different
    non-default values are a conflict.

    Args:
        panels: The panels to merge.
        explicit: The axes options of the call.

    Returns:
        The axes options to build the merged panel with, with the
            ``backend`` of the call if any.

    Raises:
        InvalidSpecError: if two panels have different non-default
            values of an option the call does not set. Also a
            ``ValueError``.
    """
    options: dict[str, Any] = dict(explicit)
    for field in fields(PanelSpec):
        name = field.name
        if name == "marks" or name in options:
            continue
        values: list[Any] = []
        for panel in panels:
            value = getattr(panel, name)
            if value != field.default and value not in values:
                values.append(value)
        if len(values) > 1:
            msg = (
                f"the figures have different values of {name}: {values}. "
                f"Set {name} in the call to layer."
            )
            raise InvalidSpecError(msg)
        if values:
            options[name] = values[0]
    return options
