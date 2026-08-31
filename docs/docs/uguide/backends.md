# Choosing a Backend

:book: This page describes how `plotmux` resolves which rendering backend to use, how to change the
default backend, and how to add a new one.

## Overview

A backend turns a backend-agnostic spec into a plotting library's native figure object (e.g. a
Matplotlib `Figure`), and knows how to export that native object to a file. `plotmux` ships with
four built-in backends:

- `"matplotlib"`: renders with [Matplotlib](https://matplotlib.org/) (the default). Requires the
  `matplotlib` extra.
- `"xy"`: renders with [`xy`](https://github.com/durandtibo/xy). Requires the `xy` extra
  (Python 3.11+).
- `"bokeh"`: renders with [Bokeh](https://bokeh.org/). Requires the `bokeh` extra. Only the
  `"html"` export format is supported: static image export (`png`/`svg`) would additionally
  require a Selenium webdriver at runtime, which is outside the scope of a `pip install bokeh`.
- `"altair"`: renders with [Altair](https://altair-viz.github.io/) (Vega-Lite). Requires the
  `altair` extra. Only the `"html"`/`"json"` export formats are supported: static image export
  (`png`/`svg`/`pdf`) would additionally require the `vl-convert-python` package, which is outside
  the scope of a `pip install altair`.

A backend is only registered if its underlying plotting library is installed, so importing
`plotmux` never fails because a backend's dependency is missing; only calling a plotting function
that needs it does.

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
...

```

This is useful to render the same plotting code with several backends, e.g. to compare their
output, without permanently changing the default:

```pycon
>>> import plotmux
>>> for name in ["matplotlib"]:  # doctest: +SKIP
...     with plotmux.backend(name):
...         plotmux.line([1, 2, 3], [1, 4, 9]).save(f"line_{name}.png")
...

```

The default backend is stored in a `contextvars.ContextVar`, so it is thread/task-local: setting it
in one thread or `asyncio` task never leaks into, or races with, another one, while still behaving
like a single process-wide default in the common single-threaded case.

## Error Handling

Requesting a backend whose underlying library is not installed raises a `RuntimeError` that lists
the currently available backends:

```pycon
>>> import plotmux
>>> plotmux.hist([1, 2, 3], backend="not_a_backend")  # doctest: +SKIP
Traceback (most recent call last):
    ...
RuntimeError: No backend registered under the name 'not_a_backend'. ...

```

## Adding a Third-Party Backend

A separate package can register a new backend without modifying `plotmux`'s source, via the
`plotmux.backends` entry-point group. The package declares an entry point pointing at a module that
calls `register_backend(...)` at import time:

```toml
[project.entry-points."plotmux.backends"]
my_backend = "my_package.plotmux_backend"
```

```python
# my_package/plotmux_backend.py
from plotmux.backends.base import Backend
from plotmux.backends.registry import register_backend


class MyBackend(Backend):
    name = "my_backend"

    def render(self, spec, **kwargs): ...

    def save(self, native, path, fmt): ...


register_backend(MyBackend())
```

`plotmux` imports every module advertised this way when it starts up, after its own built-in
`matplotlib`/`xy` backends, so a third-party backend can freely reuse those names' absence or
presence. A module that fails to import (e.g. its own underlying library is missing) is silently
skipped, mirroring how the built-in backends guard their own registration.

## What's Next

- [The Plotting API](api.md): the unified plotting functions
- [Layering Charts](layer.md): combine several charts on one set of axes
