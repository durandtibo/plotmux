# Plotting a CDF

:book: This page describes `plotmux.cdf()`, which plots the empirical cumulative distribution
function (CDF) of an array of values.

## Overview

`plotmux.cdf()` plots the fraction of `values` that fall at or below each point on the x-axis,
approximated with a binned step curve:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], title="My CDF")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

## Binning and Axis Range

`nbins` controls how many bins are used to approximate the cumulative curve. `None` (the default)
uses the backend's own default binning:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3], nbins=20)
>>> fig.save("cdf.png")  # doctest: +SKIP

```

`xmin`/`xmax` control the x-axis range, with the same semantics as `plotmux.hist()`: each can be an
explicit numeric value, a quantile string such as `"q0.1"` (the 10% quantile), or `None` to fall
back to the min/max of `values`:

```pycon
>>> import plotmux
>>> fig = plotmux.cdf([1, 2, 2, 3, 3, 3, 100], xmin="q0.0", xmax="q0.95")
>>> fig.save("cdf.png")  # doctest: +SKIP

```

## Style Arguments

`cdf` accepts the same style arguments as `hist`, `line`, and `scatter`: `title`, `xlabel`,
`ylabel`, `xscale`, `yscale`, `color`, `alpha`, `label`, `background_color`, `ymin`, `ymax`, and
`backend` (see [Common Style Arguments](api.md)). The one difference is `ylabel`, which defaults to
`"cumulative probability"` instead of `None`, since a CDF's y-axis always represents that same
quantity unless you override it. `ymin`/`ymax` are also worth calling out here specifically: bokeh's
CDF renderer otherwise hardcodes its own `0`/`1` y-axis bounds, and an explicit `ymin`/`ymax`
overrides that:

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
