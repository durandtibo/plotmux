# Choosing a Backend

:book: This page describes how `plotmux` resolves which rendering backend to use, how to change the
default backend, and how to add a new one.

## Overview

A backend turns a backend-agnostic spec into a plotting library's native figure object (e.g. a
Matplotlib `Figure`), and knows how to export that native object to a file. `plotmux` ships with
five built-in backends:

- `"matplotlib"`: renders with [Matplotlib](https://matplotlib.org/) (the default). Requires the
  `matplotlib` extra.
- `"xy"`: renders with [`xy`](https://github.com/durandtibo/xy). Requires the `xy` extra.
- `"bokeh"`: renders with [Bokeh](https://bokeh.org/). Requires the `bokeh` extra. Only the
  `"html"` export format is supported: static image export (`png`/`svg`) would additionally
  require a Selenium webdriver at runtime, which is outside the scope of a `pip install bokeh`.
- `"altair"`: renders with [Altair](https://altair-viz.github.io/) (Vega-Lite). Requires the
  `altair` extra. Only the `"html"`/`"json"` export formats are supported: static image export
  (`png`/`svg`/`pdf`) would additionally require the `vl-convert-python` package, which is outside
  the scope of a `pip install altair`.
- `"plotly"`: renders with [Plotly](https://plotly.com/python/). Requires the `plotly` extra. Only
  the `"html"`/`"json"` export formats are supported: static image export (`png`/`svg`/`pdf`) would
  additionally require the `kaleido` package, which is outside the scope of a `pip install plotly`.

A backend is only imported when it is used, so importing `plotmux` never fails because a backend's
dependency is missing; only calling a plotting function that needs it does (it raises a
`BackendNotFoundError` that names the extra to install).

## Selecting a Backend per Call

Every plotting function accepts a `backend` argument:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 3], bins=5, backend="matplotlib")
>>> fig.save("histogram.png")  # doctest: +SKIP

```

`backend=None` (the default) uses the current default backend.

## Setting the Default Backend

`plotmux.set_backend()` changes the default backend for the current thread/task:

```pycon
>>> import plotmux
>>> plotmux.set_backend("matplotlib")

```

## Temporarily Overriding the Default Backend

`plotmux.backend()` is a context manager that overrides the default backend for the duration of a
`with` block, then restores the previous default:

```pycon
>>> import plotmux
>>> with plotmux.backend("matplotlib"):
...     fig = plotmux.hist([1, 2, 3])

```

This is useful to render the same plotting code with several backends, e.g. to compare their
output, without permanently changing the default:

```pycon
>>> import plotmux
>>> for name in ["matplotlib"]:  # doctest: +SKIP
...     with plotmux.backend(name):
...         plotmux.line([1, 2, 3], [1, 4, 9]).save(f"line_{name}.png")

```

The default backend is stored in a `contextvars.ContextVar`, so it is thread/task-local: setting it
in one thread or `asyncio` task never leaks into, or races with, another one, while still behaving
like a single process-wide default in the common single-threaded case.

## Error Handling

`plotmux.set_backend()`/`plotmux.backend()` reject an unknown name immediately, at the call site,
before storing it — this catches a typo like `"mtaplotlib"` right away instead of only on the next
plotting call, at zero import cost:

```pycon
>>> import plotmux
>>> plotmux.set_backend("not_a_backend")  # doctest: +SKIP
Traceback (most recent call last):
    ...
RuntimeError: Unknown backend 'not_a_backend'. Known backends: ['altair', 'bokeh', 'matplotlib', 'plotly', 'xy']

```

A name that passes this check (a built-in name, or one advertised by an installed third-party
plugin) can still fail later, when a plotting function actually renders with it, if its underlying
library turns out not to be installed — being _known_ is not the same as being _installed_
(`plotmux.backends.available_backends()` lists the backends that can be used).
Passing such a name directly to a plotting function's `backend` argument (bypassing
`set_backend`/`backend`) raises the same error there instead:

```pycon
>>> import plotmux
>>> plotmux.hist([1, 2, 3], backend="not_a_backend")  # doctest: +SKIP
Traceback (most recent call last):
    ...
RuntimeError: No backend registered under the name 'not_a_backend'. ...

```

## Adding a Third-Party Backend

A backend is a class with three required methods: `capabilities()`, `draw(scene)` and
`save(native, path, fmt)`. It draws the three primitives of a **scene** and applies the axes style;
it does not decide any number on the screen. `plotmux.scene.build_scene(spec)` turns the spec of a
figure into an `AxesScene` (one axes) or a `GridScene` (a grid of axes): its `primitives` are `Bars`,
`Line` and `Points` (see `plotmux.primitives`), each with its resolved color and label, and the
`AxesScene` holds the title, the labels, the scales, the limits, the background color, the legend
style and the categories of the x-axis.

A separate package can add a new backend without modifying `plotmux`'s source, via the
`plotmux.backends` entry-point group. The entry point is named after the backend, and its value is
`package.module:BackendClass`:

```toml
[project.entry-points."plotmux.backends"]
my_backend = "my_package.plotmux_backend:MyBackend"
```

```python
# my_package/plotmux_backend.py
from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.primitives import Bars, Line, Points
from plotmux.scene import AxesScene, GridScene


class MyBackend(Backend):
    name = "my_backend"

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=frozenset({"png"}),  # the export formats of a figure
            grid_formats=frozenset({"png"}),  # the export formats of a grid
            legend_locations=frozenset({"top_left", "top_right"}),
            markers=frozenset({"circle", "square"}),
        )

    def draw(self, scene: AxesScene | GridScene):
        # Draw each primitive of scene.primitives (Bars, Line or Points), then apply the
        # style of the axes. A GridScene holds one AxesScene per panel in scene.panels.
        ...

    def save(self, native, path, fmt): ...

    # Optional: how `Figure.show()` displays the native figure (the default raises
    # `NotImplementedError`), and the rich display of Jupyter (the default uses the
    # `_repr_mimebundle_` or `_repr_html_`/`_repr_svg_`/`_repr_png_`/`_repr_jpeg_` of `native`).
    def show(self, native): ...

    def mimebundle(self, native): ...
```

`Backend.render(spec)` is not overridden: it builds the scene, checks it against `capabilities()`
(a legend location or a marker that the backend does not declare raises an
`UnsupportedSpecError` before anything is drawn, and `plotmux.export.save` raises an
`UnsupportedFormatError` for a format that is not declared before any file or directory is created),
then calls `draw`. A new chart type needs no change in a backend when it is a composition of `Bars`,
`Line` and `Points`, see [the developer guide](../dev/development.md).

The module is imported, and the class instantiated once, the first time the name is used (e.g.
`plotmux.hist(..., backend="my_backend")`). `import plotmux` reads no entry point and imports no
backend: none of the five built-in backends (`matplotlib`, `xy`, `bokeh`, `altair`, `plotly`) is
imported before it is requested either. `plotmux.set_backend("my_backend")` accepts the name as soon
as the package is installed, because the names of the entry points are read from the installed
metadata without importing the plugin.

A backend can also be registered from code, with `register_backend`:

```pycon
>>> from plotmux.backends import get_backend, register_backend
>>> from plotmux.backends.matplotlib.backend import MatplotlibBackend
>>> class OtherBackend(MatplotlibBackend):
...     name = "other_backend"
...
>>> register_backend(OtherBackend())
>>> get_backend("other_backend") is get_backend("other_backend")
True

```

A name already used by a registered backend or by a built-in backend is refused with a
`BackendRegistrationError`, so installing a plugin never takes over `matplotlib` by accident. To
replace a backend on purpose, call `register_backend(backend, replace=True)`. An instance registered
that way wins over the built-in backend and over a plugin of the same name.

If the library of a backend is not installed, using the backend raises a `BackendNotFoundError` that
names the extra to install (e.g. `pip install "plotmux[matplotlib]"`), and the original
`ImportError` is its `__cause__`. `plotmux.backends.available_backends()` lists the names that can
be used, without importing anything. Any other exception raised while a plugin loads (a bug in the
plugin) is not hidden: it propagates when the plugin is first used.

## What's Next

- [The Plotting API](api.md): the unified plotting functions
- [The Figure Object](figure.md): per-backend export format support, including the one `xy`/`grid`
  exception
- [Layering Charts](layer.md): combine several charts on one set of axes
