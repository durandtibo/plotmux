# Architecture

This page describes `plotmux`'s internal architecture: how it is organized, and why. See
[DESIGN.md](https://github.com/durandtibo/plotmux/blob/main/DESIGN.md) in the repository for the
full, up-to-date design document.

## Goal

`plotmux` is a lightweight abstraction layer over Python's plotting libraries: users write plotting
code once against `plotmux`'s unified API and choose the rendering backend (`matplotlib`, `xy`,
`bokeh`, `altair`, ...) at runtime. Swapping backends should be a one-line configuration change, and
adding a new backend or chart type should not require changing existing code.

The unified API targets a small set of generic, broadly-useful chart types and figure-level concerns:
the ones almost every plotting task needs (histograms, empirical CDFs, line charts, scatter
plots, layering them together, laying them out in a grid, common axis styling, per-mark color,
export), not
comprehensive coverage of every chart type a backend can draw. A niche or highly backend-specific
plot is expected to stay behind the escape hatch (`Figure.to_native()`) rather than becoming a new
spec.

## Principle: Separate Spec From Render

Two layers:

1. **Chart specs** (`plotmux.specs`): plain, backend-agnostic frozen dataclasses describing *what*
   to plot (data + encoding + style). They never import a plotting library.
2. **Backends** (`plotmux.backends`): one package per plotting library, responsible for turning a
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

Backend registration is lazy, not eager: `plotmux/__init__.py` does *not* import any of the four
built-in backend subpackages (`matplotlib`, `xy`, `bokeh`, `altair`) at `import plotmux` time.
Instead, `backends/registry.py` holds a `{name: module path}` map, and `get_backend(name)` imports
the matching submodule the first time that name is actually requested (e.g. via
`backend="matplotlib"`, or the first `plotmux.hist(...)` call after `plotmux.set_backend("xy")`);
each subpackage's `__init__.py` still calls `register_backend(...)` as an import-time side effect,
guarded by that library's `is_*_available()` check, only now triggered later. This means a process
that only ever renders with `matplotlib` never imports `xy`, `bokeh`, or `altair` (or their
underlying libraries) even if all three happen to be installed alongside it.

`plotmux/__init__.py` additionally calls `plotmux.backends.registry.load_entry_point_backends()`
once, at import time: this imports every third-party backend advertised via the `plotmux.backends`
entry-point group (see
[Adding a Third-Party Backend](../uguide/backends.md#adding-a-third-party-backend)). Since none of
the four built-ins are imported yet at that point either, a third-party plugin can freely register
under any name, built-in or not — whichever registers last for a given name wins. A plugin module
that fails to import because its own underlying library isn't installed is silently skipped
(`ImportError`); any other exception it raises while loading is caught and turned into a
`RuntimeWarning` instead of propagating, so a broken third-party plugin can only fail to register
itself, never crash `import plotmux` for every user.

`api.py` never triggers registration itself: it only calls `get_backend(name)`, which is what
actually imports a built-in submodule lazily, or raises `BackendNotFoundError` if `name` isn't
registered (typically because its library isn't installed). `config.set_backend()`/`backend()`
additionally reject a name that isn't even *known* — neither a built-in name, an
entry-point-advertised name, nor already registered — immediately, at the call site, without
importing anything (`backends/registry.py::known_backend_names()`); a name that is known but not
yet registered still only fails later, at render time, since validating that would require the
same import laziness was introduced to avoid.

## Key Components

### `BaseSpec`

Holds the figure-level fields every chart type inherits (`title`, `xlabel`, `ylabel`, `xscale`,
`yscale`) so they are defined once instead of being redeclared per chart type, and gives
`Backend.render`/the `_RENDERERS` dicts a common type to dispatch on. These fields are
`kw_only=True` so they (all defaulted) can precede a subclass's own required fields
(e.g. `HistogramSpec.values`) without violating the dataclass "no non-default field after a
default field" rule. It also owns two small helpers a concrete spec's own `__post_init__` calls
instead of reimplementing: `_normalize_color(name="color")` parses a `str | tuple | None` color
field via `parse_color` and writes the canonical RGBA value back in place (`object.__setattr__`,
since specs are frozen), and the module-level `_check_equal_length(x, y)` coerces `x`/`y` to
`np.ndarray` and raises `InvalidSpecError` if their lengths differ (shared by `LineSpec` and
`ScatterSpec`).

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
is requested, typically because its underlying plotting library is not installed.

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
renderer ignores them, since each panel keeps its own; `grid()` in `api.py` does not even expose
them as parameters.

`LayerSpec.__post_init__` also assigns successive `DEFAULT_PALETTE` entries (see
[Color Parsing](#color-parsing)) to any child spec whose own `color` field is left `None`,
skipping children that already set one explicitly. Matplotlib gets distinct per-child colors for
free from its own `Axes` color cycle when children share an axes, but `xy`/`bokeh`/`altair` do
not, so this assignment happens once, backend-agnostically, at the spec layer
(`specs/layer.py::_assign_default_colors`), rather than every backend needing its own workaround.
`GridSpec` gets no such assignment: each cell is visually independent, so there is no
shared-axes indistinguishability problem to solve there.

`xy`'s grid support is the one asymmetry across backends: `xy` has no composition primitive for
arbitrary, already-built, independent panels (`xy.facet_chart` is data-driven faceting, not this),
so `backends/xy/grid.py::render_grid` returns a small `XyGrid` (the per-cell charts, `ncols`,
`title`) instead of a bare `xy.Chart`, deferring layout to export time: `XyBackend.save` embeds
each cell's standalone HTML document in its own sandboxed `<iframe srcdoc=...>` and arranges them
with CSS grid, which makes `grid(..., backend="xy")` `"html"`-only — every other format raises
`UnsupportedFormatError` for an `XyGrid`, even though a bare (non-grid) `xy.Chart` supports the
full `supported_formats` set.

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

`set_backend()` also validates its `name` argument against `known_backend_names()` before storing
it, raising `BackendNotFoundError` immediately for a name that's neither built-in, advertised by an
installed entry-point plugin, nor already registered — this catches a typo'd backend name at the
`set_backend` call site instead of only on the next plotting call, at zero import cost (see
[Data Flow](#data-flow)); `backend(...)` inherits the same check since it calls `set_backend()`
internally.

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
