# Architecture

This page describes `plotmux`'s internal architecture: how it is organized, and why. See
[DESIGN.md](https://github.com/durandtibo/plotmux/blob/main/DESIGN.md) in the repository for the
full, up-to-date design document.

## Goal

`plotmux` is a lightweight abstraction layer over Python's plotting libraries: users write plotting
code once against `plotmux`'s unified API and choose the rendering backend (`matplotlib`, `xy`,
`bokeh`, `altair`, ...) at runtime. Swapping backends should be a one-line configuration change, and
adding a new backend or chart type should not require changing existing code.

The unified API targets a small set of generic, broadly-useful chart types and figure-level concerns
— the ones almost every plotting task needs (histograms, empirical CDFs, line charts, scatter
plots, layering them together, laying them out in a grid, common axis styling, per-mark color,
export) — not
comprehensive coverage of every chart type a backend can draw. A niche or highly backend-specific
plot is expected to stay behind the escape hatch (`Figure.to_native()`) rather than becoming a new
spec.

## Principle: Separate Spec From Render

Two layers:

1. **Chart specs** (`plotmux.specs`) — plain, backend-agnostic frozen dataclasses describing *what*
   to plot (data + encoding + style). They never import a plotting library.
2. **Backends** (`plotmux.backends`) — one package per plotting library, responsible for turning a
   spec into that library's native figure object and for exporting it to a file.

This mirrors the Vega-Lite/Altair split, and is what makes "swap backend in one line" true: because a
spec cannot hold a Matplotlib `Axes` or an `xy.Chart`, switching backends can never leak
library-specific state back into user code.

## Package Layout

```
src/plotmux/
├── utils/
│   ├── range.py                  # find_range(): quantile-or-explicit axis bounds
│   ├── cdf.py                    # compute_cdf_steps(): binned empirical CDF step vertices
│   └── imports/                  # one module per optional backend dependency
│                                  # (is_matplotlib_available(), is_xy_available(),
│                                  #  is_bokeh_available(), is_altair_available())
├── colors/
│   ├── parser.py                 # parse_color(): canonical RGBA normalization
│   ├── palette.py                # PRIMARY/SECONDARY/TERTIARY, DEFAULT_PALETTE
│   └── named.py                  # static CSS/matplotlib named-color table
├── specs/
│   ├── base.py                   # BaseSpec (title/xlabel/ylabel/xscale/yscale)
│   ├── histogram.py              # HistogramSpec
│   ├── cdf.py                    # CdfSpec
│   ├── line.py                   # LineSpec
│   ├── scatter.py                # ScatterSpec
│   ├── layer.py                  # LayerSpec (rejects nesting + empty layers)
│   └── grid.py                   # GridSpec (rejects nesting + empty cells)
├── backends/
│   ├── base.py                   # Backend ABC + dispatch helpers
│   ├── registry.py                # register_backend() / get_backend() / entry points
│   ├── matplotlib/                # MatplotlibBackend
│   ├── xy/                        # XyBackend
│   ├── bokeh/                     # BokehBackend
│   └── altair/                    # AltairBackend
├── figure.py                     # Figure wrapper
├── export.py                      # save(figure, path)
├── config.py                      # default backend + context manager
├── exceptions.py                  # PlotmuxError hierarchy
├── api.py                         # public hist(), cdf(), line(), scatter(), layer(), grid()
└── testing/fixtures.py            # pytest fixtures for downstream users
```

Every backend (`matplotlib`, `xy`, `bokeh`, `altair`) implements all six specs, including `grid.py`
and `cdf.py`.

`specs/<type>.py` plus one `_RENDERERS` entry per backend is the shape a new, similarly generic
chart type would take. A new backend adds a new `backends/<name>/` subpackage alongside the
existing ones.

## Data Flow

```
user code
   │  plotmux.hist(values, bins=30, xmin="q0.1")
   ▼
api.py             builds a HistogramSpec, resolves the active backend
   │
   ▼
specs               HistogramSpec (frozen dataclass, no plotting import)
   │
   ▼
backends/registry   get_backend("matplotlib") -> MatplotlibBackend
   │
   ▼
backends/matplotlib.backend.render(spec)  ->  native matplotlib Figure
   │
   ▼
figure.py           Figure(spec, backend_name, native)
   │
   ▼
user code           fig.show() / fig.save("out.png") / fig.to_native()
```

Backend registration is eager, not lazy: `plotmux/__init__.py` imports each built-in backend
subpackage (`matplotlib`, `xy`, `bokeh`, `altair`) for their side effect — each subpackage's
`__init__.py` calls `register_backend(...)` only if its underlying library is installed
(`is_matplotlib_available()` / `is_xy_available()` / `is_bokeh_available()` /
`is_altair_available()`). It then calls
`plotmux.backends.registry.load_entry_point_backends()`, which imports every third-party backend
advertised via the `plotmux.backends` entry-point group (see
[Adding a Third-Party Backend](../uguide/backends.md#adding-a-third-party-backend)), after the two
built-in backends so a plugin can freely reuse those names' absence or presence. So by the time
user code calls `plotmux.hist(...)`, the registry already holds every backend whose library is
installed — `api.py` only looks it up, it never triggers registration itself.

## Key Components

### `BaseSpec`

Holds the figure-level fields every chart type inherits — `title`, `xlabel`, `ylabel`, `xscale`,
`yscale` — so they are defined once instead of being redeclared per chart type, and gives
`Backend.render`/the `_RENDERERS` dicts a common type to dispatch on. These fields are
`kw_only=True` so they (all defaulted) can precede a subclass's own required fields
(e.g. `HistogramSpec.values`) without violating the dataclass "no non-default field after a
default field" rule.

### Color Parsing

`parse_color()` normalizes the color formats users already know (hex strings, CSS/Matplotlib named
colors, RGB(A) float tuples) into one canonical representation, an RGBA tuple of floats in
`[0, 1]`. A spec normalizes its own `color` field in `__post_init__`, so every backend always
receives an already-validated, canonical color. The named-color table is bundled with `plotmux`
itself, so it resolves without Matplotlib installed.

### `CdfSpec`

`CdfSpec` plots the empirical cumulative distribution function of `values`, approximated as a
binned step curve. `plotmux.utils.cdf.compute_cdf_steps()` computes the `(x, y)` step vertices
shared by every backend except matplotlib, which instead calls `Axes.hist(...,
cumulative=True, histtype="step")` directly (see `plotmux.backends.matplotlib.cdf`). Unlike the
other specs, `CdfSpec.ylabel` defaults to `"cumulative probability"` instead of `None`.

### `Backend` and the Registry

`Backend` is an ABC with two methods, `render(spec, **kwargs)` and `save(native, path, fmt)`, plus a
`supported_formats: ClassVar[frozenset[str]]` each concrete backend declares.
`resolve_renderer()` and `check_export_format()` in `backends/base.py` factor out the
lookup-or-raise dispatch logic (`{spec_type: renderer}` lookup, `{format}` membership check) shared
by every backend, so a backend only owns its dict of renderers, not the dispatch mechanics around
it. `backends/registry.py` maps a backend name to its registered instance, and raises a
`BackendNotFoundError` (also a `RuntimeError`) listing available backends when an unregistered name
is requested — typically because its underlying plotting library is not installed.

### `plotmux.exceptions`

Every exception `plotmux` raises is a `PlotmuxError`, in addition to whichever standard-library
exception type the raise site already used (`ValueError`, `RuntimeError`, `NotImplementedError`).
Each concrete exception (`InvalidSpecError`, `InvalidColorError`, `UnsupportedSpecError`,
`UnsupportedFormatError`, `ExportError`, `BackendNotFoundError`) multiply-inherits from both, so
existing `except ValueError`-style code keeps working unchanged, while new code can catch anything
`plotmux`-specific in one place with `except PlotmuxError`.

### Layering and Grid Layouts

`LayerSpec` draws multiple child specs on one shared set of axes; `GridSpec` lays out multiple
child specs as independent panels, the backend-agnostic equivalent of Matplotlib's
`pyplot.subplots()`. Both are one flat pass over their children: a `LayerSpec` nested inside
`layers`, or a `GridSpec` nested inside `cells`, is rejected in `__post_init__`, so callers must
flatten nesting themselves rather than relying on recursive dispatch. A `GridSpec` cell may itself
be a `LayerSpec`, since layering and gridding are independent, composable concerns. Each backend's
own `backends/<name>/layer.py` / `backends/<name>/grid.py` owns composing the children onto shared
axes/chart state or independent panels; every built-in backend implements both.
`GridSpec` inherits `xlabel`/`ylabel`/`xscale`/`yscale` from `BaseSpec` but every backend's grid
renderer ignores them, since each panel keeps its own — `grid()` in `api.py` does not even expose
them as parameters.

### `Figure`

The object returned to the user by every public plotting function. It is a thin wrapper holding
`spec`, `backend_name`, and `native`, plus three convenience methods: `show()`, `save(path)`
(delegating to `plotmux.export.save`), and `to_native()`, the escape hatch to backend-specific
functionality not exposed by the unified API.

### `config`

The current default backend is stored in a `contextvars.ContextVar` rather than a plain module
global, so it is thread/task-local: `set_backend()`/`backend(...)` in one thread or `asyncio` task
never leaks into or races with another one, while still behaving like a single process-wide default
in the common single-threaded case.

## Constraints From the Existing Codebase

- `coola`'s optional-dependency pattern (`is_*_available`, `*_available`, `raise_*_missing_error`)
  is reused as-is by `plotmux.utils.imports`. New backends follow the same pattern instead of
  introducing a new one.
- `matplotlib`, `xy`, `bokeh`, and `altair` are optional extras (`xy` is further gated to
  `python_version >= '3.11'` in its extra marker). Only `numpy` and `coola` are hard dependencies,
  so the core package (specs, registry, config, public API) must import cleanly with no plotting
  library installed.
- `plotmux.utils.range.find_range` implements quantile-or-explicit axis bounds (e.g. `xmin="q0.1"`)
  once, and is reused by every spec that needs it rather than reimplemented.
- Style conventions: `from __future__ import annotations`, explicit `__all__`, Google-style
  docstrings with runnable `pycon` examples, `ruff`/`black`/`pyright` clean, tests split into
  `tests/unit/` and `tests/integration/` mirroring `src/plotmux/`.

## What's Next

- [Development Guide](development.md): setting up the development environment
- [User Guide](../uguide/api.md): the public API this architecture supports
