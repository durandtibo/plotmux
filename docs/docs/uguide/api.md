# Plotting API

:book: This page describes `plotmux`'s public plotting functions: `plotmux.hist`, `plotmux.bar`,
`plotmux.stacked_bar`, `plotmux.cdf`, `plotmux.line`, `plotmux.scatter`, `plotmux.slope`,
`plotmux.layer`, and `plotmux.grid`. It explains the concepts shared by all of them: specs,
backends, common style arguments, and the `Figure` object they all return.

**Prerequisites:** You'll need to know a bit of Python.
For a refresher, see the [Python tutorial](https://docs.python.org/tutorial/).
It is helpful to know a bit of [NumPy](https://numpy.org/doc/stable/user/quickstart.html).

## Overview

`plotmux` exposes nine top-level plotting functions:

- `plotmux.hist()`: plot a histogram
- `plotmux.bar()`: plot a bar chart
- `plotmux.stacked_bar()`: plot a stacked bar chart
- `plotmux.cdf()`: plot an empirical cumulative distribution function (CDF)
- `plotmux.line()`: plot a line chart
- `plotmux.scatter()`: plot a scatter chart
- `plotmux.slope()`: plot a slope/abline reference line
- `plotmux.layer()`: combine several charts onto one shared set of axes
- `plotmux.grid()`: lay out several charts as independent panels in a grid

Each of these functions:

1. builds a backend-agnostic **spec** describing what to plot (data + encoding + style),
2. renders that spec through a **backend** (Matplotlib, `xy`, ...), resolved from the `backend`
   argument or the current default backend (see [Choosing a backend](backends.md)),
3. returns the result wrapped in a `Figure`.

## Plotting a Histogram

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=10, title="My histogram")
>>> fig.save("histogram.png")  # doctest: +SKIP

```

`bins` controls the number of histogram bins. `xmin`/`xmax` control the x-axis range: each can be
an explicit numeric value, a quantile string such as `"q0.1"` (the 10% quantile), or `None` to fall
back to the min/max of `values`:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 2, 3, 3, 3, 100], bins=10, xmin="q0.0", xmax="q0.95")
>>> fig.save("histogram.png")  # doctest: +SKIP

```

Set `density=True` to normalize the histogram so the area under it integrates to 1.

## Plotting a Bar Chart

```pycon
>>> import plotmux
>>> fig = plotmux.bar([1, 2, 3], [4, 9, 1], label="counts")
>>> fig.save("bar.png")  # doctest: +SKIP

```

`width` controls the width of each bar, in `x` data units (defaults to `0.8`). `x` can also be an
array of strings (e.g. `["a", "b", "c"]`), drawn as a categorical axis.

## Plotting a Stacked Bar Chart

```pycon
>>> import plotmux
>>> from plotmux.specs import BarSeries
>>> fig = plotmux.stacked_bar(
...     ["Apples", "Pears", "Nectarines"],
...     [BarSeries(y=[2, 1, 4], label="2015"), BarSeries(y=[1, 3, 2], label="2016")],
... )
>>> fig.save("stacked_bar.png")  # doctest: +SKIP

```

Unlike `plotmux.layer()`ing several `plotmux.bar()` calls together, which draws each bar
independently onto shared axes (they simply overlap at shared `x` positions), `stacked_bar()` draws
its `series` cumulatively: each `BarSeries` is stacked on top of the running total of the series
before it, at each `x` position — matching the "stacked bar" you'd expect from any plotting
library. `series` is a list of `plotmux.specs.BarSeries(y=..., label=None, color=None)`, one per
stacked segment, in bottom-to-top order. A series with no explicit `color` gets a distinct color
from `plotmux.colors.DEFAULT_PALETTE`, cycling in series order, so unrelated series never end up
indistinguishable by default (see [Colors](colors.md)).

## Plotting an Empirical CDF

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], title="My CDF")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

`plotmux.cdf()` plots the empirical cumulative distribution function of `values`. `nbins` controls
how many bins are used to approximate the curve (`None` uses the backend's default binning), and
`xmin`/`xmax` accept the same explicit-value/quantile-string/`None` semantics as `hist`. Unlike the
other chart functions, `ylabel` defaults to `"cumulative probability"` instead of `None`, since a
CDF's y-axis always represents that same quantity unless you override it. See [Plotting a CDF](cdf.md)
for a dedicated walkthrough.

## Plotting a Line Chart

```pycon
>>> import plotmux
>>> fig = plotmux.line([1, 2, 3], [1, 4, 9], label="y = x^2")
>>> fig.save("line.png")  # doctest: +SKIP

```

`linewidth` and `linestyle` (`"solid"`, `"dashed"`, `"dotted"`, or `"dashdot"`) control the line's
appearance.

## Plotting a Scatter Chart

```pycon
>>> import plotmux
>>> fig = plotmux.scatter([1, 2, 3], [1, 4, 9], size=20)
>>> fig.save("scatter.png")  # doctest: +SKIP

```

`size` controls the marker size, and `edgecolor` sets a separate color for the marker edge (`None`
reuses `color` for the edge too).

## Plotting a Slope / Abline

```pycon
>>> import plotmux
>>> fig = plotmux.slope(2, 10, backend="matplotlib")
>>> fig.save("slope.png")  # doctest: +SKIP

```

`plotmux.slope(gradient, intercept=0.0, ...)` draws a reference line, `y = gradient * x +
intercept`, spanning the current axes — unlike `line()`, it draws no data of its own. It typically
appears as a `layer()` child alongside a data-bound spec, e.g. a scatter plot with a fitted trend
line overlaid:

```pycon
>>> import plotmux
>>> fig = plotmux.layer(
...     plotmux.scatter([1, 2, 3, 4], [1.1, 2.0, 2.9, 4.2]),
...     plotmux.slope(1, 0),
... )
>>> fig.save("scatter_with_trend.png")  # doctest: +SKIP

```

Not every backend supports a *standalone* `plotmux.slope(...)` call: matplotlib and bokeh have a
native "line by slope, independent of data range" primitive, but altair, `xy`, and plotly need
concrete endpoints to draw from. On those three backends, `slope()` only works as a `layer()` child
next to a data-bound sibling (as in the example above) — the sibling's x-range supplies the
endpoints. A standalone `plotmux.slope(..., backend="altair")` (no data-bound sibling) raises
`NotImplementedError`. See [Choosing a Backend](backends.md) and `plotmux.backends.capabilities()`
(in [The Figure Object](figure.md)) to check this ahead of time.

## Common Style Arguments

`hist`, `bar`, `stacked_bar`, `cdf`, `line`, `scatter`, `slope`, and `layer` all accept the same
figure-level style arguments:

- `title`: an optional figure title
- `xlabel` / `ylabel`: optional axis labels
- `xscale` / `yscale`: `"linear"` (default) or `"log"`
- `background_color`: an optional figure background color, same format as `color` below. `None`
  uses the backend's default (usually white/transparent).
- `ymin` / `ymax`: an optional explicit lower/upper bound for the y-axis. `None` leaves the axis
  autoscaled. Unlike `hist`/`cdf`'s `xmin`/`xmax`, these never accept a quantile string — there is
  no single data array to resolve a quantile against at the figure level.
- `backend`: the name of the backend to render with, or `None` for the current default (see
  [Choosing a Backend](backends.md))

Every chart type that draws a mark (all but `layer`/`grid`) also accepts:

- `color`: a hex string (`"#rrggbb"` or `"#rrggbbaa"`), a CSS/Matplotlib named color
  (e.g. `"tab:blue"`), or an RGB(A) tuple of floats in `[0, 1]`. See
  [Colors](colors.md) for details.
- `label`: a label used e.g. in the legend
- `alpha`: an optional opacity in `[0, 1]`. `None` uses the backend's default (usually fully
  opaque).

```pycon
>>> import plotmux
>>> fig = plotmux.line(
...     [1, 2, 3],
...     [1, 4, 9],
...     color="tab:orange",
...     alpha=0.8,
...     title="Quadratic",
...     xlabel="x",
...     ylabel="y",
...     yscale="log",
...     background_color="white",
...     ymin=0,
... )
>>> fig.save("line.png")  # doctest: +SKIP

```

`plotmux.grid()` is the one exception: since each panel keeps its own independent axes, `grid()`
does not accept `xlabel`/`ylabel`/`xscale`/`yscale`/`background_color`/`ymin`/`ymax`/`color` at
all — only `title` (shown once above the whole grid), `ncols`, and `backend`. See
[Grid Layouts](grid.md).

A few fields only make sense for one chart type and live only on that function: `bins`/`density`
(`hist`), `width` (`bar`/`stacked_bar`), `nbins` (`cdf`), `linewidth`/`linestyle` (`line`/`slope`),
`size`/`edgecolor` (`scatter`), `gradient`/`intercept` (`slope`), `series` (`stacked_bar`).

`legend_title`, `legend_location`, and `legend_orientation` are also figure-level fields shared by
every spec, but they are not (yet) exposed as named arguments on these convenience functions; set
them by constructing the spec directly instead, e.g. `plotmux.specs.LineSpec(x=..., y=...,
legend_title="Series")` rendered via `plotmux.backends.get_backend(...).render(spec)`.

## Backend-Specific Arguments

Any extra keyword argument not recognized by the unified API is forwarded as-is to the backend's
renderer, letting you reach backend-specific options without leaving the unified API:

```pycon
>>> import plotmux
>>> fig = plotmux.hist(
...     [1, 2, 3], bins=5, histtype="step"
... )  # "histtype" is forwarded to Matplotlib
>>> fig.save("histogram.png")  # doctest: +SKIP

```

## What's Next

- [Choosing a Backend](backends.md): pick a rendering backend, or switch between them
- [Plotting a CDF](cdf.md): a dedicated walkthrough of `plotmux.cdf()`
- [Layering Charts](layer.md): combine several charts on one set of axes
- [Grid Layouts](grid.md): lay out several charts as independent panels in a grid
- [Colors](colors.md): the color formats accepted by `color` arguments
- [The Figure Object](figure.md): showing and exporting the rendered figure
