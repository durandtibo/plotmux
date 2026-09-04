r"""Contain the public plotting API."""

from __future__ import annotations

__all__ = ["bar", "cdf", "grid", "hist", "layer", "line", "scatter", "slope", "stacked_bar"]

from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from plotmux.backends.registry import get_backend
from plotmux.config import get_default_backend
from plotmux.figure import Figure
from plotmux.specs import (
    BarSeries,
    BarSpec,
    BaseSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from plotmux.colors import Color


# The ``BaseSpec``-level ``Args:`` lines shared, word for word, by every
# public plotting function that also declares a ``color`` parameter (``hist``,
# ``bar``, ``line``, ``scatter``, ``slope``). Written once here and spliced
# into each function's docstring via ``str.format`` (see the ``{_COMMON_STYLE_ARGS}``
# placeholder below) instead of being hand-copied five times, so a wording
# change is a one-site edit rather than a five-site one to keep in sync (see
# DESIGN.md, section 9.2). ``cdf`` (a different ``ymin`` note),
# ``stacked_bar``/``layer`` (a different ``background_color`` note, no
# ``color`` to refer back to) and ``grid`` (none of these fields) keep their
# own text rather than reusing this constant.
_COMMON_STYLE_ARGS = """title: An optional figure title.
    xlabel: An optional x-axis label.
    ylabel: An optional y-axis label.
    xscale: The x-axis scale, ``"linear"`` or ``"log"``.
    yscale: The y-axis scale, ``"linear"`` or ``"log"``.
    background_color: An optional figure background color. Same
        format as ``color``. ``None`` uses the backend's default.
    ymin: An optional explicit lower bound for the y-axis.
        ``None`` leaves the axis autoscaled.
    ymax: An optional explicit upper bound for the y-axis.
        ``None`` leaves the axis autoscaled.
    backend: The name of the backend to use to render the
        figure, or ``None`` to use the current default backend
        (see ``plotmux.set_backend``)."""


def _with_common_style_args(fn: Callable[..., Figure]) -> Callable[..., Figure]:
    r"""Splice ``_COMMON_STYLE_ARGS`` into a function's ``{_COMMON_STYLE_ARGS}``
    docstring placeholder.

    A decorator rather than a plain ``.format()`` call after every ``def``
    so the substitution reads the same way at each of the five call sites
    (see ``_COMMON_STYLE_ARGS`` above) and a sixth function adopting the
    shared block is a one-line addition.
    """
    assert fn.__doc__ is not None  # noqa: S101 every decorated function below has one
    fn.__doc__ = fn.__doc__.format(_COMMON_STYLE_ARGS=_COMMON_STYLE_ARGS)
    return fn


def _render(spec: BaseSpec, backend: str | None, **kwargs: Any) -> Figure:
    r"""Render a spec through a backend and wrap the result in a
    ``Figure``.

    Factors out the three steps shared by every public plotting
    function (``hist``, ``line``, ``scatter``, ``layer``): resolve the
    backend name, render the spec, wrap the native output.

    Args:
        spec: The backend-agnostic spec to render.
        backend: The name of the backend to use, or ``None`` to use
            the current default backend (see
            ``plotmux.config.get_default_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.
    """
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)


@_with_common_style_args
def hist(  # noqa: D417 the common Args entries are spliced in by _with_common_style_args
    values: Sequence[float] | np.ndarray,
    *,
    bins: int = 30,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    label: str | None = None,
    density: bool = False,
    color: Color = None,
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a histogram.

    Args:
        values: The array of values to plot.
        bins: The number of histogram bins. Must be a positive
            integer.
        xmin: Specifies the lower bound of the x-axis range. It can
            be an explicit value, a quantile string such as
            ``"q0.1"``, or ``None`` to use the minimum of ``values``.
        xmax: Specifies the upper bound of the x-axis range. Same
            semantics as ``xmin`` but for the upper bound.
        label: An optional label used e.g. in the legend.
        density: If ``True``, draw and return a probability
            density: each bin will display the bin's raw count
            divided by the total number of counts and the bin
            width, so that the area under the histogram integrates
            to 1. Defaults to ``False``.
        color: An optional color for the bars. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        alpha: An optional bar opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        {_COMMON_STYLE_ARGS}
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``bins`` is not a positive integer, ``alpha``
            is not in ``[0, 1]``, ``color``/``background_color`` is
            not a valid color, ``xmin`` and ``xmax`` are both
            explicit numeric values with ``xmin >= xmax``, or
            ``ymin``/``ymax`` are both set with ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=3)  # doctest: +SKIP

        ```
    """
    spec = HistogramSpec(
        values=np.asarray(values),
        bins=bins,
        xmin=xmin,
        xmax=xmax,
        label=label,
        density=density,
        color=color,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


@_with_common_style_args
def bar(  # noqa: D417 the common Args entries are spliced in by _with_common_style_args
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    label: str | None = None,
    color: Color = None,
    width: float = 0.8,
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a bar chart.

    Args:
        x: The array of bar positions.
        y: The array of bar heights. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the bars. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        width: The width of each bar, in ``x`` data units. Must be a
            positive number.
        alpha: An optional bar opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        {_COMMON_STYLE_ARGS}
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``width`` is not a positive number, ``alpha`` is not in
            ``[0, 1]``, ``color``/``background_color`` is not a
            valid color, or ``ymin``/``ymax`` are both set with
            ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.bar([1, 2, 3], [4, 5, 6])  # doctest: +SKIP

        ```
    """
    spec = BarSpec(
        x=np.asarray(x),
        y=np.asarray(y),
        label=label,
        color=color,
        width=width,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


def stacked_bar(
    x: Sequence[float] | Sequence[str] | np.ndarray,
    series: Sequence[BarSeries],
    *,
    width: float = 0.8,
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a stacked bar chart.

    Unlike ``layer()``'s ``BarSpec`` support, which draws several
    ``BarSpec``s independently onto shared axes (they simply overlap
    at shared ``x`` positions), this draws ``series`` cumulatively:
    each series is stacked on top of the running total of the series
    before it, at each ``x`` position. See ``plotmux.specs.
    StackedBarSpec``/``plotmux.specs.BarSeries``.

    Args:
        x: The array of bar positions, shared by every series. Either
            numeric or an array of strings, drawn as a categorical
            x-axis (e.g. ``x=["Apples", "Pears", "Nectarines"]``).
        series: The series to stack, in stacking order (bottom to
            top). Must be non-empty, and every series' ``y`` must have
            the same length as ``x``.
        width: The width of each bar, in ``x`` data units. Must be a
            positive number.
        alpha: An optional bar opacity, in ``[0, 1]``, applied to
            every series. ``None`` uses the backend's default (usually
            fully opaque).
        title: An optional figure title.
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
        background_color: An optional figure background color. Same
            format as a series' ``color``. ``None`` uses the
            backend's default.
        ymin: An optional explicit lower bound for the y-axis.
            ``None`` leaves the axis autoscaled.
        ymax: An optional explicit upper bound for the y-axis.
            ``None`` leaves the axis autoscaled.
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``series`` is empty, any series' ``y`` does
            not have the same length as ``x``, ``width`` is not a
            positive number, ``alpha`` is not in ``[0, 1]``, any
            series' ``color`` is not a valid color, or
            ``ymin``/``ymax`` are both set with ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> from plotmux.specs import BarSeries
        >>> fig = plotmux.stacked_bar(
        ...     ["Apples", "Pears", "Nectarines"],
        ...     [BarSeries(y=[2, 1, 4], label="2015"), BarSeries(y=[1, 3, 2], label="2016")],
        ... )  # doctest: +SKIP

        ```
    """
    spec = StackedBarSpec(
        x=np.asarray(x),
        series=tuple(series),
        width=width,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


def cdf(
    values: Sequence[float] | np.ndarray,
    *,
    nbins: int | None = None,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = "cumulative probability",
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot the empirical cumulative distribution function (CDF) of
    an array of values.

    Args:
        values: The array of values to plot.
        nbins: The number of bins to use to approximate the
            cumulative distribution. Must be a positive integer, or
            ``None`` to use the backend's default binning.
        xmin: Specifies the lower bound of the x-axis range. It can
            be an explicit value, a quantile string such as
            ``"q0.1"``, or ``None`` to use the minimum of ``values``.
        xmax: Specifies the upper bound of the x-axis range. Same
            semantics as ``xmin`` but for the upper bound.
        label: An optional label used e.g. in the legend.
        color: An optional color for the curve. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        alpha: An optional curve opacity, in ``[0, 1]``. ``None``
            uses the backend's default (usually fully opaque).
        title: An optional figure title.
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label. Defaults to
            ``"cumulative probability"``.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
        background_color: An optional figure background color. Same
            format as ``color``. ``None`` uses the backend's default.
        ymin: An optional explicit lower bound for the y-axis.
            ``None`` leaves the axis autoscaled (bokeh's ``CdfSpec``
            renderer hardcodes its own ``0``/``1`` bounds regardless;
            an explicit ``ymin``/``ymax`` here overrides that, see
            ``plotmux.backends.bokeh.cdf.render_cdf``).
        ymax: An optional explicit upper bound for the y-axis.
            ``None`` leaves the axis autoscaled.
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``nbins`` is set and is not a positive
            integer, ``alpha`` is not in ``[0, 1]``,
            ``color``/``background_color`` is not a valid color,
            ``xmin`` and ``xmax`` are both explicit numeric values
            with ``xmin >= xmax``, or ``ymin``/``ymax`` are both set
            with ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3])  # doctest: +SKIP

        ```
    """
    spec = CdfSpec(
        values=np.asarray(values),
        nbins=nbins,
        xmin=xmin,
        xmax=xmax,
        label=label,
        color=color,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


@_with_common_style_args
def line(  # noqa: D417 the common Args entries are spliced in by _with_common_style_args
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    label: str | None = None,
    color: Color = None,
    alpha: float | None = None,
    linewidth: float | None = None,
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid",
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a line chart.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the line. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        alpha: An optional line opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        linewidth: An optional line width. ``None`` uses the
            backend's default width.
        linestyle: The line's dash style.
        {_COMMON_STYLE_ARGS}
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``alpha`` is not in ``[0, 1]``,
            ``color``/``background_color`` is not a valid color, or
            ``ymin``/``ymax`` are both set with ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.line([1, 2, 3], [1, 4, 9])  # doctest: +SKIP

        ```
    """
    spec = LineSpec(
        x=np.asarray(x),
        y=np.asarray(y),
        label=label,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


@_with_common_style_args
def scatter(  # noqa: D417 the common Args entries are spliced in by _with_common_style_args
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    label: str | None = None,
    color: Color = None,
    size: float | None = None,
    edgecolor: Color = None,
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a scatter chart.

    Args:
        x: The array of x values.
        y: The array of y values. Must have the same length as
            ``x``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the markers. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        size: An optional marker size. ``None`` uses the backend's
            default size.
        edgecolor: An optional, separate color for the marker edge.
            Same format as ``color``. ``None`` uses ``color`` for the
            edge too.
        alpha: An optional marker opacity, in ``[0, 1]``. ``None``
            uses the backend's default (usually fully opaque).
        {_COMMON_STYLE_ARGS}
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``x`` and ``y`` do not have the same length,
            ``size`` is not a positive number, ``alpha`` is not in
            ``[0, 1]``,
            ``color``/``edgecolor``/``background_color`` is not a
            valid color, or ``ymin``/``ymax`` are both set with
            ``ymin > ymax``.

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.scatter([1, 2, 3], [1, 4, 9])  # doctest: +SKIP

        ```
    """
    spec = ScatterSpec(
        x=np.asarray(x),
        y=np.asarray(y),
        label=label,
        color=color,
        size=size,
        edgecolor=edgecolor,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


@_with_common_style_args
def slope(  # noqa: D417 the common Args entries are spliced in by _with_common_style_args
    gradient: float,
    intercept: float = 0.0,
    *,
    label: str | None = None,
    color: Color = None,
    linewidth: float | None = None,
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid",
    alpha: float | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Plot a slope (a.k.a. abline) annotation: a line defined by
    ``y = gradient * x + intercept``, spanning the current axes.

    Unlike ``line``, this draws no data of its own -- it is a
    reference/trend line. Not supported by every backend: matplotlib
    (via ``Axes.axline``) and bokeh (via ``bokeh.models.Slope``) both
    have a native "line by slope, independent of data range"
    primitive; altair and xy do not (see ``DESIGN.md``, section 8.1),
    so ``backend="altair"``/``backend="xy"`` raises
    ``UnsupportedSpecError``. It typically appears as a ``layer()``
    child alongside a data-bound spec, e.g. a scatter plot with a
    fitted trend line overlaid.

    Args:
        gradient: The line's slope.
        intercept: The line's y-intercept (the ``y`` value at
            ``x = 0``). Defaults to ``0.0``.
        label: An optional label used e.g. in the legend.
        color: An optional color for the line. It can be a hex
            string (``"#rrggbb"`` or ``"#rrggbbaa"``), a
            CSS/matplotlib named color (e.g. ``"tab:blue"``), or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default color.
        linewidth: An optional line width. ``None`` uses the
            backend's default width.
        linestyle: The line's dash style.
        alpha: An optional line opacity, in ``[0, 1]``. ``None`` uses
            the backend's default (usually fully opaque).
        {_COMMON_STYLE_ARGS}
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to the backend's renderer.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if ``alpha`` is not in ``[0, 1]``,
            ``color``/``background_color`` is not a valid color, or
            ``ymin``/``ymax`` are both set with ``ymin > ymax``.
        NotImplementedError: if the resolved backend is ``altair`` or
            ``xy`` and this ``slope(...)`` call is not layered with a
            data-bound spec (see ``layer``): standalone ``SlopeSpec``
            support remains matplotlib/bokeh only (see DESIGN.md,
            section 8.1).

    Example:
        ```pycon
        >>> import plotmux
        >>> fig = plotmux.slope(2, 10, backend="matplotlib")  # doctest: +SKIP

        ```
    """
    spec = SlopeSpec(
        gradient=gradient,
        intercept=intercept,
        label=label,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


def layer(
    *items: BaseSpec | Figure,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    background_color: Color = None,
    ymin: float | None = None,
    ymax: float | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Combine specs (or already-rendered ``Figure``s) onto one
    shared axes.

    Args:
        *items: The child specs to draw together, in draw order. A
            ``Figure`` (e.g. one returned by ``plotmux.line(...)``)
            is accepted as shorthand for its ``.spec``: only the spec
            is reused, the earlier native figure is discarded and
            everything is re-rendered together, since two independent
            native figures can't be merged after the fact in either
            backend.
        title: An optional figure title, describing the combined
            axes (not any individual child).
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
        background_color: An optional figure background color. It
            can be a hex string, a CSS/matplotlib named color, or an
            RGB(A) tuple of floats in ``[0, 1]``. ``None`` uses the
            backend's default.
        ymin: An optional explicit lower bound for the y-axis.
            ``None`` leaves the axis autoscaled.
        ymax: An optional explicit upper bound for the y-axis.
            ``None`` leaves the axis autoscaled.
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to every child's renderer call.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if no ``items`` are given, one of the given
            specs is itself a ``LayerSpec`` (nesting is not
            supported), ``background_color`` is not a valid color,
            or ``ymin``/``ymax`` are both set with ``ymin > ymax``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> import plotmux
        >>> from plotmux.specs import HistogramSpec
        >>> fig = plotmux.layer(
        ...     HistogramSpec(values=np.arange(101), bins=10),
        ...     plotmux.line([0, 100], [0, 5]),
        ... )  # doctest: +SKIP

        ```
    """
    layers = tuple(item.spec if isinstance(item, Figure) else item for item in items)
    spec = LayerSpec(
        layers=layers,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
        background_color=background_color,
        ymin=ymin,
        ymax=ymax,
    )
    return _render(spec, backend, **kwargs)


def grid(
    *items: BaseSpec | Figure,
    ncols: int = 1,
    title: str | None = None,
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Lay out specs (or already-rendered ``Figure``s) as independent
    panels in a grid.

    Unlike ``layer`` (which draws every child onto one shared axes),
    each item here gets its own, independent panel -- the
    backend-agnostic equivalent of matplotlib's ``pyplot.subplots``.
    An item may itself be built with ``layer(...)`` (several series
    sharing one panel), since layering and gridding are independent,
    composable concerns.

    Args:
        *items: The child specs to draw, one independent panel per
            item, in row-major order (left to right, top to bottom).
            A ``Figure`` (e.g. one returned by ``plotmux.line(...)``)
            is accepted as shorthand for its ``.spec``, same as
            ``layer``: only the spec is reused, the earlier native
            figure is discarded and everything is re-rendered
            together.
        ncols: The number of columns in the grid. Rows are filled
            left to right; the last row is left short when
            ``len(items)`` is not a multiple of ``ncols``. Must be a
            positive integer.
        title: An optional figure-level title, shown once above the
            whole grid (not any individual panel).
        backend: The name of the backend to use to render the
            figure, or ``None`` to use the current default backend
            (see ``plotmux.set_backend``).
        **kwargs: Additional backend-specific keyword arguments,
            forwarded to every panel's renderer call.

    Returns:
        The rendered figure.

    Raises:
        ValueError: if no ``items`` are given, one of the given specs
            is itself a ``GridSpec`` (nesting is not supported), or
            ``ncols`` is not a positive integer.

    Example:
        ```pycon
        >>> import numpy as np
        >>> import plotmux
        >>> from plotmux.specs import HistogramSpec
        >>> fig = plotmux.grid(
        ...     HistogramSpec(values=np.arange(101), bins=10),
        ...     plotmux.line([0, 100], [0, 5]),
        ...     ncols=2,
        ... )  # doctest: +SKIP

        ```
    """
    cells = tuple(item.spec if isinstance(item, Figure) else item for item in items)
    spec = GridSpec(cells=cells, ncols=ncols, title=title)
    return _render(spec, backend, **kwargs)
