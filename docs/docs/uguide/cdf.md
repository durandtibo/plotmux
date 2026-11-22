# Plotting a CDF

:book: This page describes `plotmux.cdf()`, which plots the empirical cumulative distribution
function (CDF) of an array of values.

## Overview

`plotmux.cdf()` plots `P(X <= x)`: the fraction of `values` that fall at or below each point on the
x-axis. The curve is exact, a step of `1 / n` at each of the `n` values, and it is the same on every
backend:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], title="My CDF")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

The curve has `2 n` vertices, so a very large input draws a large polyline.

## Binning Large Inputs

`nbins` is an opt-in binning that bounds the number of vertices to `2 * nbins + 1`: the values are
binned first, over their own range, and the curve is the cumulative sum of the bins. `None` (the
default) is the exact CDF:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], nbins=20)
>>> fig.save("cdf.png")  # doctest: +SKIP

```

## Range

`xmin`/`xmax` restrict the part of the curve that is drawn, with the same semantics as
`plotmux.hist()`: each can be an explicit numeric value, a quantile string such as `"q0.1"` (the 10%
quantile, computed on the finite values), or `None` to fall back to the min/max of `values`. They do
**not** renormalize the curve: the height of the curve at `x` is still the fraction of **all** the
values at or below `x`.

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3, 100], xmin="q0.0", xmax="q0.95")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

They are not axis limits either: the axes autoscale on the drawn curve. Set `ymin`/`ymax` to limit
the y-axis.

## Style Arguments

`cdf` accepts the same options as `hist`, `line`, and `scatter`: `title`, `xlabel`, `ylabel`,
`xscale`, `yscale`, `color`, `alpha`, `label`, `background_color`, `ymin`, `ymax`, the legend options
and `backend` (see [Axes Options](api.md)). The one difference is `ylabel`, which defaults to
`"cumulative probability"` instead of `None`, since a CDF's y-axis always represents that same
quantity unless you override it:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], ylabel="fraction of samples")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

## What's Next

- [The Plotting API](api.md): the other unified plotting functions, and concepts shared by all of
  them
- [Layering Charts](layer.md): e.g. overlay a CDF and a reference line on one set of axes
- [Colors](colors.md): the color formats accepted by `color`
