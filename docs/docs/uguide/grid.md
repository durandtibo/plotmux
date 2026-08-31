# Grid Layouts

:book: This page describes `plotmux.grid()`, which lays out several charts as independent panels in
a grid.

## Overview

`plotmux.grid()` accepts any number of child specs, or already-rendered `Figure`s, and lays each one
out in its own, independent panel — the backend-agnostic equivalent of Matplotlib's
`pyplot.subplots()`. This is different from [`plotmux.layer()`](layer.md), which draws every child
onto one *shared* set of axes: with `grid`, each child keeps its own axes.

```pycon
>>> import numpy as np
>>> import plotmux
>>> from plotmux.specs import HistogramSpec
>>> fig = plotmux.grid(
...     HistogramSpec(values=np.arange(101), bins=10),
...     plotmux.line([0, 100], [0, 5]),
...     ncols=2,
...     title="Two independent panels",
... )
>>> fig.save("grid.png")  # doctest: +SKIP

```

A `Figure` passed as an item, such as `plotmux.line(...)` above, is shorthand for its `.spec`: only
the spec is reused. The earlier native figure is discarded and everything is re-rendered together,
since two independent native figures can't be merged after the fact in either backend.

An item may itself be built with [`plotmux.layer()`](layer.md), since layering and gridding are
independent, composable concerns: a panel can contain several series sharing one set of axes.

## Arranging Panels

`ncols` controls the number of columns. Panels fill left to right, top to bottom, in the order the
items were given; the last row is left short (its remaining panels left empty) when the number of
items is not a multiple of `ncols`:

```pycon
>>> import plotmux
>>> fig = plotmux.grid(
...     plotmux.line([1, 2, 3], [1, 2, 3]),
...     plotmux.line([1, 2, 3], [3, 2, 1]),
...     plotmux.line([1, 2, 3], [1, 4, 9]),
...     ncols=2,
... )
>>> fig.save("grid.png")  # doctest: +SKIP

```

## Style Arguments

Unlike `hist`, `line`, `scatter`, and `layer`, `grid` only accepts `title` and `backend`, plus
`ncols`. `title` is shown once above the whole grid, not any individual panel. `xlabel`, `ylabel`,
`xscale`, `yscale`, and `color` have no meaning at the grid level since each panel keeps its own
style — set those on the child specs themselves instead.

## Restrictions

`grid` does not support nesting: passing a `GridSpec` (or a `Figure` built from one) as one of its
items raises a `ValueError`. Layout is one flat pass over `cells`, so flatten nested grids yourself
before calling `grid` rather than relying on recursive dispatch. `grid` also requires at least one
item, and `ncols` must be a positive integer.

## What's Next

- [The Plotting API](api.md): the unified plotting functions combined by `grid`
- [Layering Charts](layer.md): combine several charts onto one shared set of axes, for use as a
  single grid panel
