# Layering Charts

:book: This page describes `plotmux.layer()`, which combines several charts onto one shared set of
axes.

## Overview

`plotmux.layer()` accepts any number of marks, or single-panel `Figure`s, and draws them together on
one shared set of axes, e.g. overlaying a line on top of a histogram. A layer is a panel with several
marks:

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

A `Figure` passed as an item, such as `plotmux.line(...)` above, contributes its marks and its axes
options. The earlier native figure is discarded and everything is re-rendered together, since two
independent native figures can't be merged after the fact.

## Axes Options

Like `hist`, `line`, and `scatter`, `layer` accepts the axes options (`title`, `xlabel`, `ylabel`,
`xscale`, `yscale`, `xmin`, `xmax`, `ymin`, `ymax`, `background_color`, the legend options and
`backend`, see [The Plotting API](api.md)). They describe the combined axes.

The axes options of the figures given as items are merged, in this order:

1. an option set in the call to `layer` wins;
2. else the unique value of the figures that is not the default;
3. else, if two figures have different values, an `InvalidSpecError` asks you to set the option in
   the call.

```pycon
>>> import plotmux
>>> fig = plotmux.layer(
...     plotmux.line([1, 2, 3], [1, 2, 3], title="a trend"),
...     plotmux.scatter([1, 2, 3], [1.1, 1.9, 3.2]),
... )
>>> fig.spec.title
'a trend'
>>> plotmux.layer(
...     plotmux.line([1, 2, 3], [1, 2, 3], title="a"),
...     plotmux.line([1, 2, 3], [3, 2, 1], title="b"),
... )
Traceback (most recent call last):
    ...
plotmux.exceptions.InvalidSpecError: the figures have different values of title: ['a', 'b']. Set title in the call to layer.

```

## Layering a Slope with a Data-Bound Chart

`SlopeSpec` (a reference/trend line with no data of its own, see [The Plotting API](api.md)) is
drawn over the x extent of the panel, so it works in any layer, on every backend, as long as the
panel has an extent: the data of another mark, or `xmin`/`xmax`. Give it as a mark, not as the
figure of `plotmux.slope()` (which needs its own `xmin`/`xmax`):

```pycon
>>> import plotmux
>>> from plotmux.specs import SlopeSpec
>>> fig = plotmux.layer(
...     plotmux.scatter([1, 2, 3, 4], [1.1, 2.0, 2.9, 4.2]),
...     SlopeSpec(gradient=1, intercept=0),
...     backend="altair",
... )
>>> fig.save("scatter_with_trend.html")  # doctest: +SKIP

```

A layer with a slope and nothing else raises an `InvalidSpecError` when the panel is built, whatever
the backend, because there is nothing to compute an extent from.

## Colors in a Layer

A mark that sets no explicit `color` is assigned one from `DEFAULT_PALETTE` (see
[Colors](colors.md)), in draw order, so each mark remains visually distinguishable without you
having to pick colors by hand. A mark with an explicit color does not use a color of the palette.

## Restrictions

A layer holds marks, and a mark is not a panel, so layers do not nest in the type: passing a layer
as an item of another layer simply contributes its marks. Passing a grid raises an
`InvalidSpecError`. A categorical `x` (strings) cannot be mixed with a numeric `x` on the same axes,
and `layer` requires at least one item.

## What's Next

- [The Plotting API](api.md): the unified plotting functions combined by `layer`
- [Grid Layouts](grid.md): lay out several charts (or layers) as independent panels in a grid
- [Colors](colors.md): how colors are assigned to the marks of a layer
