# plotmux design

Status: in progress — core abstraction, histogram spec, and two
backends (matplotlib, xy) are implemented; common axis styling
(title/labels/scale) and additional chart types are designed below
but not yet built. Sections are marked ✅ implemented or 🚧 planned.
Date: 2026-08-23

## 1. Goal

plotmux is a lightweight abstraction layer over Python's plotting
libraries: users write plotting code once against plotmux's unified
API and choose the rendering backend (matplotlib, xy, ...) at
runtime. Swapping backends should be a one-line configuration change,
and adding a new backend or chart type should not require changing
existing code.

Non-goals: plotmux does not try to expose every feature of every
backend through the unified API. Backend-specific power features
remain reachable via an escape hatch (see [4.3](#43-figure)), not by
growing the common API to the union of all backends.

## 2. Constraints from the existing codebase

- `coola` is already a dependency and its optional-dependency pattern
  (`is_*_available`, `*_available`, `raise_*_missing_error`) is
  reused as-is by `src/plotmux/utils/imports/matplotlib.py` and
  `src/plotmux/utils/imports/xy.py`. New backends follow the same
  pattern instead of introducing a new one.
- `matplotlib` and `xy` are already declared as optional extras in
  `pyproject.toml` (`xy` is further gated to `python_version >= '3.11'`
  in its extra marker). Only `numpy` and `coola` are hard dependencies,
  so the core package (specs, registry, config, public API) must
  import cleanly with no plotting library installed.
- `src/plotmux/core/range.py` (`find_range`) already implements
  quantile-or-explicit axis bounds (e.g. `xmin="q0.1"`). This is
  reused by specs rather than reimplemented.
- Style conventions already in place: `from __future__ import
  annotations`, explicit `__all__`, Google-style docstrings with
  runnable `pycon` examples, `ruff`/`black`/`pyright` clean, tests
  split into `tests/unit/` and `tests/integration/` mirroring
  `src/plotmux/`.

## 3. Architecture

### 3.1 Principle: separate spec from render ✅

Two layers:

1. **Chart specs** — plain, backend-agnostic frozen dataclasses
   describing *what* to plot (data + encoding + style). They never
   import a plotting library.
2. **Backends** — one class per plotting library, responsible for
   turning a spec into that library's native figure object and for
   exporting it to a file.

This mirrors the Vega-Lite/Altair split and is what makes "swap
backend in one line" true: because a spec cannot hold a matplotlib
`Axes` or an `xy.Chart`, switching backends can never leak
library-specific state back into user code.

### 3.2 Package layout ✅ (current state)

```
src/plotmux/
├── core/
│   ├── range.py                 # find_range()
│   └── specs/
│       ├── base.py              # BaseSpec (no fields yet)
│       └── histogram.py         # HistogramSpec
├── backends/
│   ├── base.py                  # Backend ABC
│   ├── registry.py              # register_backend() / get_backend()
│   ├── matplotlib/
│   │   ├── __init__.py          # registers MatplotlibBackend if available
│   │   ├── backend.py           # MatplotlibBackend
│   │   └── histogram.py         # render_histogram(ax, spec) -> Axes
│   └── xy/
│       ├── __init__.py          # registers XyBackend if available
│       ├── backend.py           # XyBackend
│       └── histogram.py         # render_histogram(spec) -> xy.Chart
├── figure.py                    # Figure wrapper
├── export.py                    # save(figure, path)
├── config.py                    # default backend + context manager
├── api.py                       # public hist()
├── testing/fixtures.py          # shared test fixtures
└── utils/imports/               # one module per optional backend dep
                                  # (matplotlib.py, xy.py)
```

Planned additions (🚧, see [Build order](#6-build-order)):

```
├── core/specs/
│   ├── line.py                  # LineSpec
│   └── scatter.py               # ScatterSpec
├── backends/matplotlib/
│   ├── style.py                 # apply_common_style(ax, spec)
│   ├── line.py
│   └── scatter.py
└── backends/xy/
    ├── style.py
    ├── line.py
    └── scatter.py
```

### 3.3 Data flow ✅

```
user code
   │  plotmux.hist(values, bins=30, xmin="q0.1")
   ▼
api.py            builds a HistogramSpec, resolves the active backend
   │
   ▼
core/specs        HistogramSpec (frozen dataclass, no plotting import)
   │
   ▼
backends/registry  get_backend("matplotlib") -> MatplotlibBackend
   │
   ▼
backends/matplotlib.backend.render(spec)  ->  native matplotlib Figure
   │
   ▼
figure.py         Figure(spec, backend_name, native)
   │
   ▼
user code         fig.show() / fig.save("out.png") / fig.to_native()
```

Registration itself is eager, not lazy: `plotmux/__init__.py` imports
`plotmux.backends.matplotlib` and `plotmux.backends.xy` for their side
effect (each subpackage's `__init__.py` calls `register_backend(...)`
only if `is_matplotlib_available()` / `is_xy_available()` is `True`).
So by the time user code calls `plotmux.hist(...)`, the registry
already holds every backend whose library is installed — `api.py`
only looks it up, it never triggers registration itself.

## 4. Key components

### 4.1 `BaseSpec` — 🚧 common fields planned, ✅ mechanism in place

`BaseSpec` today is an empty frozen dataclass — a marker base class
that documents the contract ("plain data, no plotting-library import,
validate in `__post_init__`") and gives `Backend.render` / the
`_RENDERERS` dicts a common type to dispatch on:

```python
@dataclass(frozen=True)
class BaseSpec:
    """Base class for chart specs. No fields of its own yet."""


@dataclass(frozen=True)
class HistogramSpec(BaseSpec):
    values: np.ndarray
    bins: int = 30
    xmin: float | str | None = None
    xmax: float | str | None = None
    label: str | None = None
    density: bool = False
```

`xmin`/`xmax` are resolved through the existing `find_range` so the
quantile-string convention (`"q0.1"`) is defined once, in `core/`,
and reused by every spec and every backend. Validation (`bins > 0`)
happens in `__post_init__`, so an invalid spec fails before any
backend is touched.

Planned: move `title`, `xlabel`, `ylabel`, `xscale`, `yscale` onto
`BaseSpec` as common figure-level fields every chart type inherits,
so they are defined once instead of being redeclared per chart type:

```python
@dataclass(frozen=True)
class BaseSpec:
    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    xscale: Literal["linear", "log"] = "linear"
    yscale: Literal["linear", "log"] = "linear"
```

#### 4.1.1 Axis labels, title, and linear/log scale — 🚧 planned

Not implemented yet: today `HistogramSpec` has no `title`/`xlabel`/
`ylabel`/`xscale`/`yscale` fields and `api.hist()` does not accept
them. The design below is the target for when they land.

These are figure-level concerns, not encoding channels, so they will
live on `BaseSpec` and be applied the same way regardless of chart
type:

```python
plotmux.hist(values, title="Latency distribution", xlabel="ms", ylabel="count")
plotmux.line(x, y, yscale="log")
```

Each backend's `render()` will draw the chart-specific mark first (via
its per-type renderer, e.g. `render_histogram`), then apply these
common fields in one shared, backend-owned helper — for matplotlib,
`backends/matplotlib/style.py::apply_common_style(ax, spec)`:

```python
def apply_common_style(ax: Axes, spec: BaseSpec) -> Axes:
    if spec.title is not None:
        ax.set_title(spec.title)
    if spec.xlabel is not None:
        ax.set_xlabel(spec.xlabel)
    if spec.ylabel is not None:
        ax.set_ylabel(spec.ylabel)
    ax.set_xscale(spec.xscale)
    ax.set_yscale(spec.yscale)
    return ax
```

`MatplotlibBackend.render()` will call `apply_common_style` right
after dispatching to the per-type renderer, so a new chart type gets
title/label/scale support for free — its renderer only needs to draw
the mark, not handle axis styling. The xy backend implements the same
helper against `xy`'s own layout/axis API, keeping the log/linear
vocabulary (`"linear"`, `"log"`) identical across backends even
though the underlying calls differ.

`xscale`/`yscale` will default to `"linear"` rather than `None`
because, unlike title/labels, an axis always has *some* scale — there
is no meaningful "unset" state to skip, so the field is non-optional
and the backend always calls `set_xscale`/`set_yscale`.

### 4.2 `Backend` ✅

```python
class Backend(ABC):
    name: ClassVar[str]

    @abstractmethod
    def render(self, spec: BaseSpec, **kwargs: Any) -> Any: ...
    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None: ...
```

`Backend` is an ABC rather than a `Protocol`: a `Protocol` cannot
uniformly describe subclasses that dispatch `render` differently
per spec type without upsetting static type checkers. Each concrete
backend implements `render` via a `dict[type[BaseSpec], Callable]`
lookup keyed on the spec's concrete type (`MatplotlibBackend._RENDERERS`,
`XyBackend._RENDERERS` — both currently map only `HistogramSpec`).
Adding a new chart type to a backend means adding one entry to that
dict; it never grows an if/elif chain and never requires touching
other backends.

Each backend also owns its own `_SUPPORTED_FORMATS` frozenset and
checks it in `save()` before delegating to the native library
(matplotlib: `png`/`svg`/`pdf`/`jpg`/`jpeg`; xy: those plus `webp`/
`html`), so an unsupported format raises early with a clear message.

### 4.3 `Figure` ✅

Thin wrapper returned to the user: `(spec, backend_name, native)`.

- `.show()` — calls `native.show()` if the native object exposes it,
  otherwise raises `NotImplementedError`.
- `.save(path)` — delegates to `export.save`, which infers the format
  from the file suffix and calls `backend.save(native, path, fmt)`.
- `.to_native()` — returns the underlying matplotlib `Figure` /
  `xy.Chart`.

`to_native()` is the deliberate escape hatch: it keeps the common API
small without trapping users who need one backend-specific feature.

### 4.4 Backend registry ✅

`backends/registry.py` holds a `name -> Backend` mapping
(`_REGISTRY: dict[str, Backend]`). Each backend subpackage's
`__init__.py` registers its own instance at import time, guarded by
that library's `is_*_available()` check (same pattern as
`utils/imports/matplotlib.py`); `plotmux/__init__.py` imports both
`plotmux.backends.matplotlib` and `plotmux.backends.xy` for this side
effect so every installed backend is registered as soon as `plotmux`
is imported. Requesting an unregistered backend raises a `RuntimeError`
naming the requested backend and listing the currently-registered
ones.

### 4.5 `config.py` ✅

```python
plotmux.set_backend("matplotlib")  # process-wide default

with plotmux.backend("xy"):
    fig = plotmux.hist(values)  # scoped override
```

`set_backend`/`get_default_backend` hold a module-level string
(`_DEFAULT_BACKEND`, default `"matplotlib"`); `backend(name)` is a
context manager that swaps it and restores the previous value on
exit, including when the block raises. This is the concrete mechanism
behind "swapping backends is a one-line change." Note this only picks
a *name*; it does not itself validate that a backend is registered —
that check happens in `get_backend` at render time.

### 4.6 Public API (`api.py`) — ✅ `hist()`, 🚧 `line()`/`scatter()`

Only `hist()` exists today:

```python
def hist(
    values,
    *,
    bins=30,
    xmin=None,
    xmax=None,
    label=None,
    density=False,
    backend=None,
    **kwargs,
) -> Figure:
    spec = HistogramSpec(
        values=np.asarray(values),
        bins=bins,
        xmin=xmin,
        xmax=xmax,
        label=label,
        density=density,
    )
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)
```

Once [4.1.1](#411-axis-labels-title-and-linearlog-scale) lands,
`title`/`xlabel`/`ylabel`/`xscale`/`yscale` will be added to this
signature and to `line()`/`scatter()` with identical names and
defaults, since they map straight onto `BaseSpec` fields shared by
all specs. Specs and backends remain directly importable for advanced
use; `api.py` is only the convenience surface most users touch.

### 4.7 Export (`export.py`) ✅

`save(figure, path)` sanitizes `path` (via `coola.utils.path.sanitize_path`),
infers the format from the file suffix (`.png`, `.svg`, `.html`, ...),
creates the parent directory if needed, and delegates to
`backend.save(native, path, fmt)`. Each backend declares the formats
it supports (see [4.2](#42-backend)), so requesting an unsupported
format raises inside `backend.save`, and a path with no suffix raises
in `export.save` before any backend is touched.

## 5. Why this shape

- **Works for any backend, not just today's two**: nothing outside a
  `backends/<name>/` subpackage may special-case a backend by name.
  `Figure`, `export.py`, `config.py`, and `api.py` only ever go
  through `Backend`'s interface (`render`, `save`,
  `_SUPPORTED_FORMATS`) and the registry (`get_backend`,
  `register_backend`) — never `if backend_name == "matplotlib"`. This
  is why adding `xy` required zero changes to any of those four
  modules, and it is the bar any future backend (plotly, bokeh, ...)
  must also clear.
- **Extensibility without breaking existing code**: a new backend is
  a new subpackage plus one registry entry (proven twice already:
  matplotlib, then xy); a new chart type is a new spec plus one
  `_RENDERERS` entry per backend. Neither touches the other, and once
  [4.1.1](#411-axis-labels-title-and-linearlog-scale) lands, common
  axis styling (title/labels/scale) will be handled once per backend
  via `apply_common_style`, not once per chart type.
- **Optional dependencies stay optional**: `core/`, `figure.py`,
  `config.py`, `api.py`, `export.py` are always importable; every
  backend subpackage is gated behind its own `utils/imports/*` guard,
  consistent with the `matplotlib`/`xy` extras already declared in
  `pyproject.toml`. `tests/unit/backends/matplotlib/test_init.py` and
  `tests/unit/backends/xy/test_init.py` cover the "library not
  installed -> no registration" path.
- **Testability**: specs are plain dataclasses, cheap to unit test
  without a real plotting library installed (same style as
  `tests/unit/core/test_range.py`). Backend rendering gets a thinner,
  separate test layer, mirroring the existing
  `tests/unit/utils/imports` vs `tests/integration/utils/imports`
  split.
- **No leaky abstraction trap**: `Figure.to_native()` means "unified
  API" doesn't have to mean "least common denominator forever."

## 6. Build order

1. ✅ `core/specs/` (`HistogramSpec` first, since `find_range` already
   existed for it) + unit tests.
2. ✅ `backends/base.py` + `backends/registry.py`.
3. ✅ `backends/matplotlib/` implementing histogram, reusing
   `utils/imports/matplotlib.py`.
4. ✅ `figure.py`, `config.py`, `api.py` — wired `plotmux.hist(...)`
   end to end.
5. ✅ A second backend (`xy`) to prove the abstraction holds before
   adding more chart types.
6. 🚧 `style.py::apply_common_style` (title/labels/scale) for
   matplotlib and xy — see [4.1.1](#411-axis-labels-title-and-linearlog-scale).
   Do this before step 7 so `LineSpec`/`ScatterSpec` inherit working
   styling from day one instead of two chart types needing a follow-up
   migration.
7. 🚧 `LineSpec` / `ScatterSpec` + matplotlib and xy renderers.
8. 🚧 `export.py` format coverage for the new chart types (already
   generic, but worth an explicit test per chart type x format).
9. 🚧 A third backend (see [6.1](#61-candidate-future-backends)) once
   two chart types exist on both current backends, to confirm the
   abstraction still holds under more surface area.

### 6.1 Candidate future backends

matplotlib (static, the ecosystem default) and xy (interactive HTML)
already anchor opposite ends of the space plotmux needs to cover.
Ranked by likely value as backend #3+:

- **plotly** (`plotly.graph_objects`) — the other major interactive
  option; large existing user base, native Jupyter/dash support,
  export to standalone HTML like xy. Most likely next backend: it
  would be the first real test of whether "one interactive backend
  already covered by xy" makes a `Backend` implementation genuinely
  redundant, or whether xy and plotly diverge enough (API shape,
  export formats, hover/zoom semantics) to justify both.
- **bokeh** — interactive, server-callback-oriented; useful if plotmux
  ever needs live/streaming figures, which neither matplotlib nor xy
  nor plotly target well. Lower priority until there's a concrete
  streaming use case.
- **altair** (Vega-Lite) — declarative grammar-of-graphics API,
  closest in spirit to plotmux's own spec/backend split. Attractive
  as a design reference even before/instead of being implemented,
  since `BaseSpec` already mirrors its philosophy.
- **plotnine** (ggplot2-style) — matches users coming from R; mostly
  static like matplotlib, so lower priority than plotly/bokeh unless
  there is specific user demand.

None of these are scheduled; each is a `backends/<name>/` subpackage
plus a `utils/imports/<name>.py` guard plus one `pyproject.toml`
extra, following the matplotlib/xy precedent exactly — see the
backend-agnostic rule in [Section 5](#5-why-this-shape). Picking one
should be driven by actual user requests, not by this list.

## 7. Open questions

- Should `Figure` support combining multiple specs on one axes (e.g.
  overlaying a line and a scatter), or is that deferred to a later
  `Layer`/`Composite` spec?
- Resolved: `xy` already produces interactive HTML output
  (`_SUPPORTED_FORMATS` includes `"html"`), and this needed no
  xy-specific handling in `Figure`/`export.save` — both are generic
  over the backend's declared `_SUPPORTED_FORMATS` and `save`
  signature already. Any backend that wants to support a new format
  (HTML, PDF, ...) just adds it to its own `_SUPPORTED_FORMATS`; no
  other layer changes. Keep it this way: `Figure`, `export.py`, and
  `config.py` must stay backend-agnostic — no `if backend_name ==
  "xy"` branches anywhere outside the `backends/xy/` subpackage.
- Title/labels/linear-log scale are designed to live on `BaseSpec`
  (see [4.1.1](#411-axis-labels-title-and-linearlog-scale)) but are
  not implemented. Should other style defaults (color cycles, fonts)
  follow the same per-spec-field pattern, or live on `config.py` as a
  global theme instead? Per-spec fields are simple but don't let a
  user set one color palette for a whole session the way
  `set_backend` sets one backend for a whole session.
- `config.backend()`/`set_backend()` accept any string and only fail
  at render time via `get_backend`. Is that late failure acceptable,
  or should `set_backend`/`backend()` validate against the registry
  eagerly so a typo'd backend name fails at the call site instead of
  the next plot call?
