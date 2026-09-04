# Layering Charts

:book: This page describes `plotmux.layer()`, which combines several charts onto one shared set of
axes.

## Overview

`plotmux.layer()` accepts any number of child specs, or already-rendered `Figure`s, and draws them
together on one shared set of axes, e.g. overlaying a line on top of a histogram:

```pycon
>>> import numpy as np
>>> import plotmux
>>> from plotmux.specs import HistogramSpec
>>> fig = plotmux.layer(
...     HistogramSpec(values=np.arange(101), bins=10),
...     plotmux.line([0, 100], [0, 5]),
...     title="Histogram with a reference line",
... )
>>> fig.save("layered.png")  # doctest: +SKIP

```

A `Figure` passed as an item, such as `plotmux.line(...)` above, is shorthand for its `.spec`: only
the spec is reused. The earlier native figure is discarded and everything is re-rendered together,
since two independent native figures can't be merged after the fact in either backend.

## Style Arguments

Like `hist`, `line`, and `scatter`, `layer` accepts `title`, `xlabel`, `ylabel`, `xscale`, `yscale`,
`background_color`, `ymin`, `ymax`, and `backend` (see [The Plotting API](api.md)).
These describe the combined axes, not any individual child: a child's own `title` (if it has one) is
ignored when it is drawn as part of a layer.

## Layering a Slope with a Data-Bound Chart

`plotmux.slope()` (a reference/trend line with no data of its own, see [The Plotting
API](api.md)) is the one spec type that is standalone-supported on only
two of the five backends (matplotlib, bokeh). Layering it alongside a data-bound sibling makes it
work on the other three (altair, `xy`, plotly) too: the sibling's x-range supplies the concrete
endpoints `SlopeSpec` itself has none of.

```pycon
>>> import plotmux
>>> fig = plotmux.layer(
...     plotmux.scatter([1, 2, 3, 4], [1.1, 2.0, 2.9, 4.2]),
...     plotmux.slope(1, 0),
...     backend="altair",
... )
>>> fig.save("scatter_with_trend.html")  # doctest: +SKIP

```

A `layer()` with only `SlopeSpec` children (no data-bound sibling to derive a range from) still
raises `NotImplementedError` on altair/`xy`/plotly, since there is nothing to compute a range from.

## Colors in a Layer

A child spec that sets no explicit `color` is assigned one from `DEFAULT_PALETTE` (see
[Colors](colors.md)), in draw order, so each child remains visually distinguishable without you
having to pick colors by hand.

## Restrictions

`layer` does not support nesting: passing a `LayerSpec` as one of its items raises a `ValueError`.
Layering is one flat pass over its children, so flatten nested layers yourself before calling
`layer` rather than relying on recursive dispatch. `layer` also requires at least one item.

## What's Next

- [The Plotting API](api.md): the unified plotting functions combined by `layer`
- [Grid Layouts](grid.md): lay out several charts (or layers) as independent panels in a grid
- [Colors](colors.md): how colors are assigned to layer children
