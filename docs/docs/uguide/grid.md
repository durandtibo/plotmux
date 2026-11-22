# Grid Layouts

:book: This page describes `plotmux.grid()`, which lays out several charts as independent panels in
a grid.

## Overview

`plotmux.grid()` accepts any number of panels, marks, or single-panel `Figure`s, and lays each one
out in its own, independent panel (the backend-agnostic equivalent of Matplotlib's
`pyplot.subplots()`). This is different from [`plotmux.layer()`](layer.md), which draws every item
onto one _shared_ set of axes: with `grid`, each item keeps its own axes.

```pycon
>>> import numpy as np
>>> import plotmux
>>> from plotmux.specs import HistogramSpec
>>> fig = plotmux.grid(
...     HistogramSpec(values=np.arange(101), bins=10),
...     plotmux.line([0, 100], [0, 5], title="a line"),
...     ncols=2,
...     title="Two independent panels",
... )
>>> fig.save("grid.png")  # doctest: +SKIP

```

A mark (such as the histogram above) is wrapped in a default panel. A `Figure` passed as an item,
such as `plotmux.line(...)` above, contributes its panel with its own title, labels, scales and
limits. The earlier native figure is discarded and everything is re-rendered together.

A panel may hold several marks, since layering and gridding are independent, composable concerns: a
panel can contain several series sharing one set of axes, whatever the marks (a slope and a stacked
bar included):

```pycon
>>> import plotmux
>>> fig = plotmux.grid(
...     plotmux.layer(plotmux.line([1, 2, 3], [1, 2, 3]), plotmux.scatter([1, 2, 3], [1, 2, 3])),
...     plotmux.slope(1, 0, xmin=0, xmax=3),
...     ncols=2,
... )
>>> len(fig.spec.panels)
2

```

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
style: set those on the panels themselves instead (a misspelled or unsupported keyword is a
`TypeError`).

The legend and the plot background are per panel on `matplotlib`, `bokeh`, `altair` and `xy`. `plotly`
has one legend per figure, so a grid takes the legend style of its first panel that has a legend; the
background of a panel is a rectangle below its traces.

## Restrictions

A grid holds panels, and a panel holds marks, so a grid cannot be nested in the type: passing a
`GridSpec` (or a `Figure` built from one) as one of the items raises an `InvalidSpecError`. `grid`
also requires at least one item, and `ncols` must be a positive integer.

## The `xy` Backend Is HTML-Only for Grids

`xy` has no primitive for arranging arbitrary, already-built, independent panels side by side (its
`facet_chart` repeats one fixed chart per value of a data column, which is a different thing), so
`grid(..., backend="xy")` lays out each panel's standalone chart as a sandboxed HTML `<iframe>`
at export time instead of producing a single rasterizable native figure. As a result,
`fig.save(...)` only accepts an `.html` path for an `xy` grid, and every other format raises an
`UnsupportedFormatError` before any file or directory is created. This is declared in
`Backend.capabilities().grid_formats`, and `fig.supported_formats` of a grid reads it. Every other
backend supports its full usual set of formats for `grid()` too.
See [The Figure Object](figure.md#saving-a-figure) for the full per-backend format table.

## What's Next

- [The Plotting API](api.md): the unified plotting functions combined by `grid`
- [Layering Charts](layer.md): combine several charts onto one shared set of axes, for use as a
  single grid panel
