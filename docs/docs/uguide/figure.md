# The Figure Object

:book: This page describes `Figure`, the object returned by every `plotmux` plotting function, and
how to display, save, or escape to the native figure it wraps.

## Overview

`plotmux.hist()`, `plotmux.line()`, `plotmux.scatter()`, `plotmux.bar()`, `plotmux.layer()`, and
`plotmux.grid()` all return a `Figure`. It keeps three things together:

- `spec`: the backend-agnostic spec that was rendered
- `backend_name`: the name of the backend that rendered it
- `native`: the backend's native figure object (e.g. a Matplotlib `Figure`)

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5)
>>> fig.backend_name
'matplotlib'

```

## Displaying a Figure

`Figure.show()` displays the figure using the backend's default viewer:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5)
>>> fig.show()  # doctest: +SKIP

```

If the native object does not support `.show()`, a `NotImplementedError` is raised.

## Saving a Figure

`Figure.save()` saves the figure to a file. The export format is inferred from the file suffix
(e.g. `.png`, `.svg`, `.pdf`), and the parent directory is created automatically if it doesn't
already exist:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5)
>>> fig.save("output/histogram.png")  # doctest: +SKIP

```

A path with no suffix raises a `ValueError`, since the export format cannot be inferred. Supported
formats depend on the backend:

| Backend        | Supported formats                                |
|----------------|----------------------------------------------------|
| `matplotlib`   | `png`, `svg`, `pdf`, `jpg`, `jpeg`                 |
| `xy`           | `png`, `jpg`, `jpeg`, `webp`, `svg`, `pdf`, `html`  |
| `bokeh`        | `html`                                             |
| `altair`       | `html`, `json`                                     |

One exception to this table: a `plotmux.grid(..., backend="xy")` figure only supports `"html"`,
even though the `xy` backend otherwise supports the full row above. `xy` has no primitive for
composing arbitrary, already-built panels side by side, so a grid is laid out at export time as
sandboxed HTML iframes rather than a rasterizable native object; see [Grid Layouts](grid.md) for
details.

Requesting an unsupported format raises a `ValueError` listing the formats the backend supports.
Check `fig.supported_formats` ahead of time to avoid relying on that error for control flow:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5, backend="matplotlib")
>>> sorted(fig.supported_formats)
['jpeg', 'jpg', 'pdf', 'png', 'svg']

```

`plotmux.export.save()` is the underlying function called by `Figure.save()`, if you need to call it
directly with a `Figure` you already have.

## Displaying a Figure in Jupyter

`Figure` displays itself automatically as the last expression of a Jupyter cell, exactly as its
`native` object would on its own: it forwards the IPython/Jupyter rich-display dunder methods
(`_repr_html_`, `_repr_mimebundle_`, `_repr_svg_`, `_repr_jpeg_`, `_repr_png_`) to `native`, so no
extra call is needed beyond leaving `fig` as a cell's last expression. This forwarding is
restricted to that fixed set of methods, so a typo like `fig.sav(...)` still raises a clear
`AttributeError` instead of silently forwarding to `native`.

## Escaping to the Native Figure

`Figure.to_native()` returns the backend's native figure object, the escape hatch to reach
backend-specific functionality not exposed by the unified API:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5)
>>> mpl_fig = fig.to_native()  # a matplotlib.figure.Figure

```

Use this when you need a backend-specific feature that `plotmux`'s unified API does not cover,
rather than growing the common API to the union of every backend.

## What's Next

- [The Plotting API](api.md): the functions that return a `Figure`
- [Choosing a Backend](backends.md): which backend renders `native`
