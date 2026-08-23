# plotmux design

Status: proposed
Date: 2026-08-23

## 1. Goal

plotmux is a lightweight abstraction layer over Python's plotting
libraries: users write plotting code once against plotmux's unified
API and choose the rendering backend (Matplotlib, Plotly, ...) at
runtime. Swapping backends should be a one-line configuration change,
and adding a new backend or chart type should not require changing
existing code.

Non-goals: plotmux does not try to expose every feature of every
backend through the unified API. Backend-specific power features
remain reachable via an escape hatch (see [4.3](#43-figure)), not by
growing the common API to the union of all backends.

## 2. Constraints from the existing codebase

- `coola` is already a dependency and its optional-dependency pattern
  is already used in `src/plotmux/utils/imports/matplotlib.py`
  (`is_matplotlib_available`, `matplotlib_available`,
  `raise_matplotlib_missing_error`). New backends follow the same
  pattern instead of introducing a new one.
- `matplotlib` and `xy` are already declared as optional extras in
  `pyproject.toml`. Only `numpy` and `coola` are hard dependencies, so
  the core package (specs, registry, config, public API) must import
  cleanly with no plotting library installed.
- `src/plotmux/core/range.py` (`find_range`) already implements
  quantile-or-explicit axis bounds (e.g. `xmin="q0.1"`). This is
  reused by specs rather than reimplemented.
- Style conventions already in place: `from __future__ import
  annotations`, explicit `__all__`, Google-style docstrings with
  runnable `pycon` examples, `ruff`/`black`/`pyright` clean, tests
  split into `tests/unit/` and `tests/integration/` mirroring
  `src/plotmux/`.

## 3. Architecture

### 3.1 Principle: separate spec from render

Two layers:

1. **Chart specs** — plain, backend-agnostic frozen dataclasses
   describing *what* to plot (data + encoding + style). They never
   import a plotting library.
2. **Backends** — one class per plotting library, responsible for
   turning a spec into that library's native figure object and for
   exporting it to a file.

This mirrors the Vega-Lite/Altair split and is what makes "swap
backend in one line" true: because a spec cannot hold a matplotlib
`Axes` or a plotly `Figure`, switching backends can never leak
library-specific state back into user code.

### 3.2 Package layout

```
src/plotmux/
├── core/
│   ├── range.py                 # existing: find_range()
│   └── specs/
│       ├── base.py              # BaseSpec
│       ├── histogram.py         # HistogramSpec
│       ├── line.py              # LineSpec
│       └── scatter.py           # ScatterSpec
├── backends/
│   ├── base.py                  # Backend protocol
│   ├── registry.py              # register_backend() / get_backend()
│   └── matplotlib/
│       ├── backend.py           # MatplotlibBackend
│       ├── histogram.py         # HistogramSpec -> matplotlib Axes
│       ├── line.py
│       └── scatter.py
├── figure.py                    # Figure wrapper
├── export.py                    # save(figure, path)
├── config.py                    # default backend + context manager
├── api.py                       # public hist(), line(), scatter()
└── utils/imports/               # existing pattern; grows one module
                                  # per new backend dependency
```

### 3.3 Data flow

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
backends/matplotlib.backend.render(spec)  ->  native matplotlib Figure/Axes
   │
   ▼
figure.py         Figure(spec, backend_name, native)
   │
   ▼
user code         fig.show() / fig.save("out.png") / fig.to_native()
```

## 4. Key components

### 4.1 `BaseSpec`

Frozen dataclass, one field per encoding channel. Example:

```python
@dataclass(frozen=True)
class HistogramSpec(BaseSpec):
    values: np.ndarray
    bins: int = 30
    xmin: float | str | None = None
    xmax: float | str | None = None
    label: str | None = None
```

`xmin`/`xmax` are resolved through the existing `find_range` so the
quantile-string convention (`"q0.1"`) is defined once, in `core/`,
and reused by every spec and every backend.

Validation (e.g. `bins > 0`) happens in `__post_init__`, so an invalid
spec fails before any backend is touched.

### 4.2 `Backend`

```python
class Backend(Protocol):
    name: ClassVar[str]

    def render(self, spec: BaseSpec, **kwargs: Any) -> Any: ...
    def save(self, native: Any, path: Path, fmt: str) -> None: ...
```

Each concrete backend implements `render` via
`functools.singledispatchmethod`, dispatching on the spec's concrete
type. Adding a new chart type to a backend means adding one
`@render.register` method; it never grows an if/elif chain and never
requires touching other backends.

### 4.3 `Figure`

Thin wrapper returned to the user: `(spec, backend_name, native)`.

- `.show()` — delegates to the backend.
- `.save(path)` — delegates to `export.save`.
- `.to_native()` — returns the underlying matplotlib/plotly object.

`to_native()` is the deliberate escape hatch: it keeps the common API
small without trapping users who need one backend-specific feature.

### 4.4 Backend registry

`backends/registry.py` holds a `name -> Backend` mapping. A backend
module registers itself only if its library is importable, guarded
the same way `utils/imports/matplotlib.py` already guards matplotlib
(`*_available()` check + `lru_cache`). Requesting an unregistered
backend raises the same style of error as
`raise_matplotlib_missing_error()`.

### 4.5 `config.py`

```python
plotmux.set_backend("matplotlib")  # process-wide default

with plotmux.backend("plotly"):
    fig = plotmux.line(x, y)  # scoped override
```

This is the concrete mechanism behind "swapping backends is a
one-line change."

### 4.6 Public API (`api.py`)

```python
def hist(values, *, bins=30, xmin=None, xmax=None, backend=None, **style) -> Figure:
    spec = HistogramSpec(values=values, bins=bins, xmin=xmin, xmax=xmax, **style)
    return _render(spec, backend)
```

`line()` and `scatter()` follow the same shape. Specs and backends
remain directly importable for advanced use; `api.py` is only the
convenience surface most users touch.

### 4.7 Export (`export.py`)

`save(figure, path)` infers the format from the file suffix (`.png`,
`.svg`, `.html`, ...) and delegates to `backend.save`. Each backend
declares the formats it supports (matplotlib: png/svg/pdf; a future
plotly backend: html/png), so requesting an unsupported format raises
early with a clear message rather than failing inside the backend
library.

## 5. Why this shape

- **Extensibility without breaking existing code**: a new backend is
  a new subpackage plus one registry entry; a new chart type is a new
  spec plus one `render.register` per backend. Neither touches the
  other.
- **Optional dependencies stay optional**: `core/`, `figure.py`,
  `config.py`, `api.py` are always importable; every backend
  subpackage is gated behind its own `utils/imports/*` guard,
  consistent with the `matplotlib`/`xy` extras already declared in
  `pyproject.toml`.
- **Testability**: specs are plain dataclasses, cheap to unit test
  without a real plotting library installed (same style as
  `tests/unit/core/test_range.py`). Backend rendering gets a thinner,
  separate test layer, mirroring the existing
  `tests/unit/utils/imports` vs `tests/integration/utils/imports`
  split.
- **No leaky abstraction trap**: `Figure.to_native()` means "unified
  API" doesn't have to mean "least common denominator forever."

## 6. Build order

1. `core/specs/` (`HistogramSpec` first, since `find_range` already
   exists for it) + unit tests.
2. `backends/base.py` + `backends/registry.py`.
3. `backends/matplotlib/` implementing histogram, reusing
   `utils/imports/matplotlib.py`.
4. `figure.py`, `config.py`, `api.py` — wire `plotmux.hist(...)` end
   to end.
5. `LineSpec` / `ScatterSpec` + matplotlib renderers.
6. `export.py` for PNG/SVG.
7. A second backend (plotly, for HTML/interactive export) to prove
   the abstraction holds before adding more chart types.

## 7. Open questions

- Should `Figure` support combining multiple specs on one axes (e.g.
  overlaying a line and a scatter), or is that deferred to a later
  `Layer`/`Composite` spec?
- Does the plotly backend need its own `Figure` subtype for
  interactivity (zoom/hover callbacks), or does the base `Figure`
  wrapper suffice with `to_native()` as the escape hatch?
- Where should style defaults (color cycles, fonts) live — on
  `config.py` as a global theme, or per-spec only?
