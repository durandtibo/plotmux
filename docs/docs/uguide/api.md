# Plotting API

:book: This page describes `plotmux`'s public plotting functions: `plotmux.hist`, `plotmux.bar`,
`plotmux.stacked_bar`, `plotmux.cdf`, `plotmux.line`, `plotmux.scatter`, `plotmux.slope`,
`plotmux.layer`, and `plotmux.grid`. It explains the concepts shared by all of them: marks and
panels, backends, the axes options, and the `Figure` object they all return.

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

1. builds a backend-agnostic **mark** (what is drawn: the data and its style, for example a
   `HistogramSpec`) and wraps it in a **panel** (one set of axes: a `PanelSpec`),
2. renders that panel through a **backend** (Matplotlib, `xy`, ...), resolved from the `backend`
   argument or the current default backend (see [Choosing a backend](backends.md)),
3. returns the result wrapped in a `Figure`.

A backend only draws three primitives (bars, lines and points) and applies the axes style. The
numbers on the screen (the bins of a histogram, the steps of a CDF, the stacking of a bar chart,
the default colors) are decided once, before the backend is called, so the same call draws the
same chart on every backend. Swapping the backend is a one-line change.

## Plotting a Histogram

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=10, title="My histogram")
>>> fig.save("histogram.png")  # doctest: +SKIP

```

`bins` controls the number of histogram bins. `xmin`/`xmax` are the **range of the values that are
binned**: each can be an explicit numeric value, a quantile string such as `"q0.1"` (the 10%
quantile), or `None` to fall back to the min/max of `values`. They are not axis limits: the axes
autoscale on the bars that are drawn.

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

`width` controls the width of each bar, in `x` data units (defaults to `0.8`), on every backend.
`x` can also be an array of strings (e.g. `["a", "b", "c"]`), drawn as a categorical axis, in which
case `width` is a fraction of the band of a category.

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

`stacked_bar()` draws its `series` cumulatively: each `BarSeries` is stacked on top of the running
total of the series before it (a plain cumulative sum, so negative values are not handled
specially), at each `x` position. `series` is a list of
`plotmux.specs.BarSeries(y=..., label=None, color=None)`, one per stacked segment, in bottom-to-top
order. A series with no explicit `color` gets the next color of `plotmux.colors.DEFAULT_PALETTE`
(see [Colors](colors.md)). A stacked bar chart works standalone, in a layer and in a grid on every
backend.

## Plotting an Empirical CDF

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], title="My CDF")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

`plotmux.cdf()` plots the exact empirical cumulative distribution function `P(X <= x)` of `values`.
See [Plotting a CDF](cdf.md) for the binning option `nbins` and the range `xmin`/`xmax`. The `ylabel`
defaults to `"cumulative probability"` instead of `None`.

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

`size` controls the marker size, `edgecolor` sets a separate color for the marker edge (`None` reuses
`color` for the edge too), `marker` is one of `"circle"`, `"square"`, `"triangle"`, `"diamond"`,
`"cross"` and `"x"`, and `fill=False` draws hollow markers.

## Plotting a Slope / Abline

```pycon
>>> import plotmux
>>> fig = plotmux.slope(2, 10, xmin=0, xmax=5)
>>> fig.save("slope.png")  # doctest: +SKIP

```

`plotmux.slope(gradient, intercept=0.0, ...)` draws a reference line, `y = gradient * x +
intercept`. It has no data of its own, so it is drawn over the **x extent of its panel**: the
`xmin`/`xmax` of the panel where they are set, else the extent of the data of the other marks of the
panel. A panel with a slope and no extent raises an `InvalidSpecError` when it is built:

```pycon
>>> import plotmux
>>> plotmux.slope(2, 10)
Traceback (most recent call last):
    ...
plotmux.exceptions.InvalidSpecError: a mark needs the x extent of the panel (a slope has no data of its own): set xmin and xmax, or add a mark with numeric x data to the panel

```

The rule is the same on every backend, standalone, in a layer and in a grid. In a layer, the data of
the siblings gives the extent, so a trend line over a scatter plot needs no `xmin`/`xmax`:

```pycon
>>> import plotmux
>>> from plotmux.specs import SlopeSpec
>>> fig = plotmux.layer(
...     plotmux.scatter([1, 2, 3, 4], [1.1, 2.0, 2.9, 4.2]),
...     SlopeSpec(gradient=1, intercept=0),
... )
>>> fig.save("scatter_with_trend.png")  # doctest: +SKIP

```

`matplotlib` and `bokeh` draw a slope as a native infinite line, which keeps extending when you zoom
past the extent; the other backends draw the segment of the extent. See [Layering Charts](layer.md).

## Non-finite Values (`NaN` and `inf`)

The same input gives the same figure on every backend, so `plotmux` checks `NaN` and `inf` when the
spec is built, not in the plotting library:

| Input                                           | Result                                                               |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| `hist`/`cdf`: `NaN` or `inf` among the values   | Dropped, with a `UserWarning` that gives the count (once per figure) |
| `hist`/`cdf`: no finite value left              | `InvalidSpecError`                                                   |
| `hist`/`cdf`: non-numeric values                | `InvalidSpecError`                                                   |
| `hist`/`cdf`: a quantile bound (`xmin="q0.1"`)  | Computed on the finite values                                        |
| `line`/`scatter`: `NaN` in `x` or `y`           | Kept: a gap in the line, no point                                    |
| `line`/`scatter`: `inf` or `-inf` in `x` or `y` | `InvalidSpecError`                                                   |
| a panel: a categorical `x` mixed with a numeric | `InvalidSpecError`                                                   |

```pycon
>>> import warnings
>>> import plotmux
>>> with warnings.catch_warnings(record=True) as caught:
...     warnings.simplefilter("always")
...     fig = plotmux.hist([1.0, 2.0, float("nan"), 3.0], bins=3)
...
>>> str(caught[0].message)
'HistogramSpec: 1 non-finite value(s) (NaN or inf) detected in values and filtered out'
>>> fig.spec.marks[0].values
array([1., 2., 3.])

```

`InvalidSpecError` is also a `ValueError`.

## Axes Options

`hist`, `bar`, `stacked_bar`, `cdf`, `line`, `scatter`, `slope`, and `layer` all accept the same
axes options. They are declared once, as the typed dictionary `plotmux.api.PanelOptions` (and
`BoundedPanelOptions` for the functions with `xmin`/`xmax`), and map to the fields of
`plotmux.specs.PanelSpec`:

- `title`: an optional axes title
- `xlabel` / `ylabel`: optional axis labels
- `xscale` / `yscale`: `"linear"` (default) or `"log"`
- `ymin` / `ymax`: an optional explicit lower/upper limit of the y-axis. `None` leaves the axis
  autoscaled. They never accept a quantile string.
- `background_color`: an optional axes background color, same format as `color` below. `None` uses
  the backend's default.
- `legend_title`, `legend_location`, `legend_orientation`: the style of the legend, which exists if
  and only if at least one mark has a `label`. `legend_location` is one of `"top_left"`,
  `"top_right"`, `"bottom_left"`, `"bottom_right"`, `"top"`, `"bottom"`, `"left"` and `"right"`
  (there is no `"best"`: three backends have no automatic placement, and `None` uses the default
  of the library). `legend_orientation` is `"vertical"` or `"horizontal"`.
- `backend`: the name of the backend to render with, or `None` for the current default (see
  [Choosing a Backend](backends.md))

`bar`, `stacked_bar`, `line`, `scatter`, `slope` and `layer` also accept `xmin`/`xmax`, the explicit
limits of the x-axis. `hist` and `cdf` do not: their `xmin`/`xmax` are the range of the data they
bin or plot.

Every chart type that draws a mark also accepts:

- `color`: a hex string (`"#rrggbb"` or `"#rrggbbaa"`), a CSS/Matplotlib named color
  (e.g. `"tab:blue"`), or an RGB(A) tuple of floats in `[0, 1]`. `None` takes the next color of the
  default palette, so the color of a chart is the same on every backend. See
  [Colors](colors.md) for details.
- `label`: a label used in the legend
- `alpha`: an optional opacity in `[0, 1]`. `None` uses the backend's default (usually fully
  opaque).

```pycon
>>> import plotmux
>>> fig = plotmux.line(
...     [1, 2, 3],
...     [1, 4, 9],
...     color="tab:orange",
...     alpha=0.8,
...     label="y",
...     title="Quadratic",
...     xlabel="x",
...     ylabel="y",
...     yscale="log",
...     background_color="white",
...     legend_location="top_left",
...     ymin=1,
... )
>>> fig.save("line.png")  # doctest: +SKIP

```

A few fields only make sense for one chart type and live only on that function: `bins`/`density`
(`hist`), `width` (`bar`/`stacked_bar`), `nbins` (`cdf`), `linewidth`/`linestyle` (`line`/`slope`),
`size`/`edgecolor`/`marker`/`fill` (`scatter`), `gradient`/`intercept` (`slope`), `series`
(`stacked_bar`).

`plotmux.grid()` accepts no axes option: each panel keeps its own. It takes only `title` (shown once
above the whole grid), `ncols`, and `backend`. See [Grid Layouts](grid.md).

## Unknown Keyword Arguments

There is no keyword pass-through to the plotting library: a call means the same on every backend. A
misspelled or library-specific keyword is a `TypeError` of `plotmux` at the call site:

```pycon
>>> import plotmux
>>> plotmux.hist([1, 2, 3], histtype="step")
Traceback (most recent call last):
    ...
TypeError: hist() got an unexpected keyword argument 'histtype'. The axes options are: ...

```

To set an option of the library, modify the native figure after the render with
`Figure.to_native()` (see [The Figure Object](figure.md)).

## What's Next

- [Choosing a Backend](backends.md): pick a rendering backend, or switch between them
- [Plotting a CDF](cdf.md): a dedicated walkthrough of `plotmux.cdf()`
- [Layering Charts](layer.md): combine several charts on one set of axes
- [Grid Layouts](grid.md): lay out several charts as independent panels in a grid
- [Colors](colors.md): the color formats accepted by `color` arguments
- [The Figure Object](figure.md): showing and exporting the rendered figure
