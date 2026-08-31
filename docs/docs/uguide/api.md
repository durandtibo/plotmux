# Plotting API

:book: This page describes `plotmux`'s public plotting functions: `plotmux.hist`, `plotmux.cdf`,
`plotmux.line`, `plotmux.scatter`, `plotmux.layer`, and `plotmux.grid`. It explains the concepts
shared by all of them: specs, backends, common style arguments, and the `Figure` object they all
return.

**Prerequisites:** You'll need to know a bit of Python.
For a refresher, see the [Python tutorial](https://docs.python.org/tutorial/).
It is helpful to know a bit of [NumPy](https://numpy.org/doc/stable/user/quickstart.html).

## Overview

`plotmux` exposes six top-level plotting functions:

- `plotmux.hist()`: plot a histogram
- `plotmux.cdf()`: plot an empirical cumulative distribution function (CDF)
- `plotmux.line()`: plot a line chart
- `plotmux.scatter()`: plot a scatter chart
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

## Plotting a Scatter Chart

```pycon
>>> import plotmux
>>> fig = plotmux.scatter([1, 2, 3], [1, 4, 9], size=20)
>>> fig.save("scatter.png")  # doctest: +SKIP

```

## Common Style Arguments

`hist`, `cdf`, `line`, and `scatter` all accept the same figure-level style arguments:

- `title`: an optional figure title
- `xlabel` / `ylabel`: optional axis labels
- `xscale` / `yscale`: `"linear"` (default) or `"log"`
- `color`: a hex string (`"#rrggbb"` or `"#rrggbbaa"`), a CSS/Matplotlib named color
  (e.g. `"tab:blue"`), or an RGB(A) tuple of floats in `[0, 1]`. See
  [Colors](colors.md) for details.
- `label`: a label used e.g. in the legend

```pycon
>>> import plotmux
>>> fig = plotmux.line(
...     [1, 2, 3],
...     [1, 4, 9],
...     color="tab:orange",
...     title="Quadratic",
...     xlabel="x",
...     ylabel="y",
...     yscale="log",
... )
>>> fig.save("line.png")  # doctest: +SKIP

```

## Backend-Specific Arguments

Any extra keyword argument not recognized by the unified API is forwarded as-is to the backend's
renderer, letting you reach backend-specific options without leaving the unified API:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5, alpha=0.5)  # "alpha" is forwarded to Matplotlib
>>> fig.save("histogram.png")  # doctest: +SKIP

```

## What's Next

- [Choosing a Backend](backends.md): pick a rendering backend, or switch between them
- [Plotting a CDF](cdf.md): a dedicated walkthrough of `plotmux.cdf()`
- [Layering Charts](layer.md): combine several charts on one set of axes
- [Grid Layouts](grid.md): lay out several charts as independent panels in a grid
- [Colors](colors.md): the color formats accepted by `color` arguments
- [The Figure Object](figure.md): showing and exporting the rendered figure
