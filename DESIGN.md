# plotmux design

Status: in progress — core abstraction, four chart specs (histogram,
line, scatter, layer), two backends (matplotlib, xy), per-mark color
(`parse_color`), common axis styling (title/labels/scale,
`apply_common_style`), and layering multiple specs on one axes
(`plotmux.layer()`) are implemented; a third backend is designed below
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
- `src/plotmux/utils/range.py` (`find_range`) already implements
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
│   └── range.py                 # find_range()
├── colors.py                    # parse_color()
├── specs/
│   ├── base.py                  # BaseSpec (title/xlabel/ylabel/xscale/yscale)
│   ├── histogram.py             # HistogramSpec
│   ├── line.py                  # LineSpec
│   ├── scatter.py               # ScatterSpec
│   └── layer.py                  # LayerSpec (rejects nesting + empty layers)
├── backends/
│   ├── base.py                  # Backend ABC
│   ├── registry.py              # register_backend() / get_backend()
│   ├── matplotlib/
│   │   ├── __init__.py          # registers MatplotlibBackend if available
│   │   ├── backend.py           # MatplotlibBackend
│   │   ├── style.py             # apply_common_style(ax, spec)
│   │   ├── histogram.py         # render_histogram(ax, spec) -> Axes
│   │   │                         # (color: RGBA passthrough, no conversion needed)
│   │   ├── line.py               # render_line(ax, spec) -> Axes
│   │   ├── scatter.py            # render_scatter(ax, spec) -> Axes
│   │   └── layer.py              # render_layer(ax, spec) -> shared Axes
│   └── xy/
│       ├── __init__.py          # registers XyBackend if available
│       ├── backend.py           # XyBackend
│       ├── style.py             # rgba_to_xy(); apply_common_style(chart, spec)
│       ├── histogram.py         # render_histogram(spec) -> xy.Chart
│       ├── line.py               # render_line(spec) -> xy.Chart
│       ├── scatter.py            # render_scatter(spec) -> xy.Chart
│       └── layer.py              # render_layer(spec) -> composed xy.Chart
├── figure.py                    # Figure wrapper
├── export.py                    # save(figure, path)
├── config.py                    # default backend + context manager
├── api.py                       # public hist(), line(), scatter(), layer()
├── testing/fixtures.py          # shared test fixtures
└── utils/imports/               # one module per optional backend dep
                                  # (matplotlib.py, xy.py)
```

`specs/line.py`, `specs/scatter.py`, `specs/layer.py`, and the
matching `backends/matplotlib/{line,scatter,layer}.py` /
`backends/xy/{line,scatter,layer}.py` renderers are now implemented —
see steps 8-9 above and
[4.8](#48-layering-multiple-specs-on-one-axes). No further chart-type
additions are planned in this package layout; a third backend (see
[6.1](#61-candidate-future-backends)) would add a new
`backends/<name>/` subpackage alongside `matplotlib/` and `xy/`.

### 3.3 Data flow ✅

```
user code
   │  plotmux.hist(values, bins=30, xmin="q0.1")
   ▼
api.py            builds a HistogramSpec, resolves the active backend
   │
   ▼
specs        HistogramSpec (frozen dataclass, no plotting import)
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

### 4.1 `BaseSpec` — ✅ implemented

`BaseSpec` holds the common figure-level fields every chart type
inherits — `title`, `xlabel`, `ylabel`, `xscale`, `yscale` — so they
are defined once instead of being redeclared per chart type, and
gives `Backend.render` / the `_RENDERERS` dicts a common type to
dispatch on:

```python
@dataclass(frozen=True)
class BaseSpec:
    title: str | None = field(default=None, kw_only=True)
    xlabel: str | None = field(default=None, kw_only=True)
    ylabel: str | None = field(default=None, kw_only=True)
    xscale: Literal["linear", "log"] = field(default="linear", kw_only=True)
    yscale: Literal["linear", "log"] = field(default="linear", kw_only=True)


@dataclass(frozen=True)
class HistogramSpec(BaseSpec):
    values: np.ndarray
    bins: int = 30
    xmin: float | str | None = None
    xmax: float | str | None = None
    label: str | None = None
    density: bool = False
    color: ... = None
```

These fields are `kw_only=True` so they (all defaulted) can precede a
subclass's own required, non-default fields (e.g.
`HistogramSpec.values`) without violating the dataclass rule that a
non-default field cannot follow a default one — callers already pass
them by keyword (`plotmux.hist(..., title=...)`), so this changes no
call site.

`xmin`/`xmax` are resolved through the existing `find_range` so the
quantile-string convention (`"q0.1"`) is defined once, in `core/`,
and reused by every spec and every backend. Validation (`bins > 0`)
happens in `__post_init__`, so an invalid spec fails before any
backend is touched.

#### 4.1.1 Axis labels, title, and linear/log scale — ✅ implemented

These are figure-level concerns, not encoding channels, so they live
on `BaseSpec` and are applied the same way regardless of chart type:

```python
plotmux.hist(values, title="Latency distribution", xlabel="ms", ylabel="count")
plotmux.line(x, y, yscale="log")
```

Each backend's `render()` draws the chart-specific mark first (via its
per-type renderer, e.g. `render_histogram`), then applies these common
fields in one shared, backend-owned helper — for matplotlib,
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

`MatplotlibBackend.render()` calls `apply_common_style` right after
dispatching to the per-type renderer, so a new chart type gets
title/label/scale support for free — its renderer only needs to draw
the mark, not handle axis styling.

The xy backend implements the same helper against `xy`'s own
layout/axis API (`backends/xy/style.py::apply_common_style(chart,
spec)`), keeping the log/linear vocabulary (`"linear"`, `"log"`)
identical across backends even though the underlying calls differ.
One xy-specific wrinkle: `xy.Chart` is structure-immutable (see its
own `append()` docstring), so `apply_common_style` builds a *new*
`Chart` — same `kind` and existing `children` (the mark(s) already
drawn) plus an appended `xy.x_axis(label=..., type_=...)` /
`xy.y_axis(...)` pair — rather than mutating `chart` in place. Layout
(`width`/`height`/`padding`/`data`) is copied over explicitly from the
input chart; other `Chart` constructor arguments are deliberately
*not* reflected generically via `getattr`/introspection, because
several (e.g. `select`) are stored under a private attribute name
specifically because the public name collides with a same-named
`Chart` method (`Chart.select()`) — a generic copy would silently
pick up the bound method instead of the stored value.

`xscale`/`yscale` default to `"linear"` rather than `None` because,
unlike title/labels, an axis always has *some* scale — there is no
meaningful "unset" state to skip, so the field is non-optional and
the backend always calls `set_xscale`/`set_yscale` (matplotlib) or
always passes `type_` (xy).

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

### 4.6 Public API (`api.py`) — ✅ `hist()`, `line()`, `scatter()`

```python
def hist(
    values,
    *,
    bins=30,
    xmin=None,
    xmax=None,
    label=None,
    density=False,
    color=None,
    title=None,
    xlabel=None,
    ylabel=None,
    xscale="linear",
    yscale="linear",
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
        color=color,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
    )
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)
```

`line(x, y, *, label=None, color=None, ...)` and `scatter(x, y, *,
label=None, color=None, size=None, ...)` follow the same shape:
build the matching spec (`LineSpec`/`ScatterSpec`), resolve the
backend, render, wrap in a `Figure`. Both accept
`title`/`xlabel`/`ylabel`/`xscale`/`yscale` with identical names and
defaults as `hist()`, since they map straight onto `BaseSpec` fields
shared by all specs — no per-function special-casing needed. `size`
is `ScatterSpec`-only, following the precedent of `bins`/`density`
being `HistogramSpec`-only: fields that don't apply to every chart
type live on that chart type's own spec, not on `BaseSpec`. Specs and
backends remain directly importable for advanced use; `api.py` is
only the convenience surface most users touch.

### 4.7 Export (`export.py`) ✅

`save(figure, path)` sanitizes `path` (via `coola.utils.path.sanitize_path`),
infers the format from the file suffix (`.png`, `.svg`, `.html`, ...),
creates the parent directory if needed, and delegates to
`backend.save(native, path, fmt)`. Each backend declares the formats
it supports (see [4.2](#42-backend)), so requesting an unsupported
format raises inside `backend.save`, and a path with no suffix raises
in `export.save` before any backend is touched. Because this path is
generic over any spec type, no code here needed to change as chart
types were added (histogram -> +line/scatter -> +layer, steps 6-9);
step 10 added explicit test coverage — a chart-type x format matrix
per backend, see [Build order](#6-build-order) — to confirm that
genericity actually holds rather than only assuming it from the
design.

### 4.8 Layering multiple specs on one axes — ✅ implemented

plotmux supports combining multiple specs on one axes (e.g. a line
overlaid with a scatter). This needed no new mechanism in `Backend` or
`figure.py` — it fits the existing spec/backend split as one more spec
type:

```python
@dataclass(frozen=True)
class LayerSpec(BaseSpec):
    r"""A spec that draws multiple child specs on one shared axes."""

    layers: tuple[BaseSpec, ...]

    def __post_init__(self) -> None:
        if not self.layers:
            msg = "layers must contain at least one spec"
            raise ValueError(msg)
        if any(isinstance(child, LayerSpec) for child in self.layers):
            msg = "layers must not contain a LayerSpec (nesting is not supported)"
            raise ValueError(msg)
```

Nesting (a `LayerSpec` inside `layers`) is rejected rather than
supported — this resolves the corresponding item in
[Open questions](#7-open-questions): every `render_layer` does one
flat pass over `layers`, dispatching each child by its concrete type,
so allowing a nested `LayerSpec` would force every backend's
`render_layer` to recurse for a case with no current caller need;
callers must flatten nested layers themselves.

Public API:

```python
def layer(
    *items: BaseSpec | Figure,
    title=None,
    xlabel=None,
    ylabel=None,
    xscale="linear",
    yscale="linear",
    backend: str | None = None,
    **kwargs: Any,
) -> Figure:
    r"""Combine specs (or already-rendered Figures) onto one axes."""
    layers = tuple(item.spec if isinstance(item, Figure) else item for item in items)
    spec = LayerSpec(
        layers=layers,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xscale=xscale,
        yscale=yscale,
    )
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)
```

Accepting `Figure` as well as bare specs lets `plotmux.layer(fig1,
fig2)` read naturally when the user already called `plotmux.line(...)`
/ `plotmux.scatter(...)` separately; only their `.spec` is reused —
the earlier native objects are discarded and everything is re-rendered
together, since two independent native figures can't be merged after
the fact in either backend. `title`/`xlabel`/`ylabel`/`xscale`/`yscale`
are exposed the same way as on `hist()`/`line()`/`scatter()`, since
they describe the combined axes, not any individual child.

**Backend side: no interface change.** Each backend already dispatches
on `type(spec)` via its `_RENDERERS` dict (see [4.2](#42-backend)), so
supporting layering is one more entry, `LayerSpec -> render_layer`,
per backend — same pattern as adding any chart type:

- **matplotlib** (`backends/matplotlib/layer.py`): create one `Axes`,
  then call each child's existing `render_<type>(ax, child_spec)`
  function against that same `Axes`, in `layers` order, via a small
  `_AX_RENDERERS` dict local to `layer.py` (mirrors
  `MatplotlibBackend._RENDERERS`, restricted to the non-layer types).
  This is why `render_histogram(ax, spec)`/`render_line(ax, spec)`/
  `render_scatter(ax, spec)` already take an `Axes` rather than
  creating their own figure — layering was designed in from the
  start. No extra `ax.legend()` call is needed at the end: each child
  renderer already calls `ax.legend()` when its own `label` is set,
  and matplotlib's `Axes.legend()` collects every currently-plotted
  labeled artist at call time (not just the artist just added), so
  the last labeled child's own call ends up reflecting the full
  combined legend for free.
- **xy** (`backends/xy/layer.py`): xy has no chart-composition operator
  (no `chart_a + chart_b`, unlike Altair — verified against the
  installed `xy` version, resolving the corresponding item in
  [Open questions](#7-open-questions)), so each child spec is rendered
  independently via its own `render_<type>(child_spec)`, and only its
  mark children are kept (each per-type renderer returns a
  single-mark `Chart` with no axes yet — axes are added once, for the
  combined chart, by `apply_common_style`). Those marks are combined
  into one `Chart` via `xy.chart(*marks)`, xy's generic multi-mark
  composer (the same primitive `xy.line_chart`/`xy.scatter_chart`/
  `xy.histogram_chart` build on, just not fixed to one mark kind).

`apply_common_style` (see [4.1.1](#411-axis-labels-title-and-linearlog-scale))
is applied once to the combined result, not once per child — by
`Backend.render`/`MatplotlibBackend.render`, exactly as for every
other spec type, so `render_layer` itself never calls it.
`title`/`xlabel`/`ylabel`/`xscale`/`yscale` on `LayerSpec` itself
describe the combined axes, and per-child style fields (if any layer
sets its own) only affect that child's marks.

Constraints are deliberately not enforced by `LayerSpec` itself (e.g.
mixing a `HistogramSpec` with incompatible axis semantics): validating
"do these children make sense together" is a backend/domain concern,
not something `specs` can know without importing plotting-library
context, consistent with [3.1](#31-principle-separate-spec-from-render).

### 4.9 Specifying colors across backends — ✅ implemented

Same problem as [4.1.1](#411-axis-labels-title-and-linearlog-scale)
(one vocabulary, N backend-native representations), but `color` is a
per-mark encoding, not a figure-level concern, so it follows the
precedent of `label` and lives on each chart-type spec, not on
`BaseSpec`:

```python
@dataclass(frozen=True)
class HistogramSpec(BaseSpec):
    ...
    color: (
        str | tuple[float, float, float] | tuple[float, float, float, float] | None
    ) = None
```

**Canonical input, one parser, reused everywhere** — mirrors how
`xmin`/`xmax` funnel through the single `find_range` in `core/`
instead of every spec/backend reimplementing quantile parsing.
`colors.py::parse_color` accepts the formats users already know
and that both matplotlib and xy already understand as *input*:

- a hex string, `"#rrggbb"` or `"#rrggbbaa"`
- a CSS/matplotlib named color, `"tab:blue"`, `"crimson"`, ...
  (validated against `matplotlib.colors.CSS4_COLORS` — a static table,
  so this validation works even when the matplotlib *backend* isn't
  registered, since it's a `matplotlib_available()`-gated import in
  `colors.py`, not a call into a `Backend`)
- an RGB(A) tuple of floats in `[0, 1]`, matplotlib's own convention

`parse_color` normalizes any of these to one canonical representation,
an RGBA tuple of floats in `[0, 1]`, and raises `ValueError` on
anything else (out-of-range floats, unknown names, malformed hex) —
so a bad color fails in spec `__post_init__`, before any backend is
touched, same as an invalid `bins`.

**Canonical representation, N backend-native encoders.** Each backend
converts the normalized RGBA tuple to whatever its native call
expects, in its own `style.py` (see [4.1.1](#411-axis-labels-title-and-linearlog-scale)):

- matplotlib accepts `(r, g, b, a)` floats in `[0, 1]` directly —
  `ax.hist(..., color=spec.color)` needs no conversion once
  `spec.color` is already a `parse_color` output.
- xy's mark `color` parameter accepts a CSS color string (verified
  against `xy`'s own `_parse_color`, which resolves a CSS string via
  its native grammar) — `backends/xy/style.py::rgba_to_xy(color:
  tuple[float, float, float, float]) -> str` converts the canonical
  RGBA tuple to `"rgba(r, g, b, a)"` with `r`/`g`/`b` as `0`-`255`
  ints, so the translation lives next to the backend it's for, not in
  `core/`.

This keeps `core/` matplotlib-*format*-shaped (RGBA `[0, 1]` is just a
convenient universal wire format, not a matplotlib dependency) without
making `core/` matplotlib-*library*-dependent for every input shape,
and it means adding a color format later (e.g. HSL) only touches
`parse_color`, never a backend.

Multiple series or multiple `LayerSpec` children defaulting to
*distinct* colors when the user sets no `color` at all (a color
*cycle*, not an explicit color) is a separate, harder problem — see
[Open questions](#7-open-questions): matplotlib gets this for free
from its own default cycle when children share an `Axes` (see
[4.8](#48-layering-multiple-specs-on-one-axes)), but there is no
agreed cross-backend cycle vocabulary yet, so it's out of scope for
this section, which only covers a user setting one explicit `color`.

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
  `_RENDERERS` entry per backend. Neither touches the other, and
  common axis styling (title/labels/scale) is handled once per
  backend via `apply_common_style`, not once per chart type — see
  [4.1.1](#411-axis-labels-title-and-linearlog-scale).
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

1. ✅ `specs/` (`HistogramSpec` first, since `find_range` already
   existed for it) + unit tests.
2. ✅ `backends/base.py` + `backends/registry.py`.
3. ✅ `backends/matplotlib/` implementing histogram, reusing
   `utils/imports/matplotlib.py`.
4. ✅ `figure.py`, `config.py`, `api.py` — wired `plotmux.hist(...)`
   end to end.
5. ✅ A second backend (`xy`) to prove the abstraction holds before
   adding more chart types.
6. ✅ `colors.py::parse_color` + `color` field on `HistogramSpec` +
   matplotlib/xy per-type renderer support — see
   [4.9](#49-specifying-colors-across-backends). Self-contained (only
   touches the existing histogram renderers), so it ships before the
   larger style step below rather than being bundled with it.
7. ✅ `style.py::apply_common_style` (title/labels/scale) for
   matplotlib and xy — see [4.1.1](#411-axis-labels-title-and-linearlog-scale).
   Done before step 8 so `LineSpec`/`ScatterSpec` inherit working
   styling *and* color from day one instead of needing a follow-up
   migration.
8. ✅ `LineSpec` / `ScatterSpec` + matplotlib and xy renderers,
   reusing `parse_color` and `apply_common_style` from steps 6-7, plus
   `plotmux.line()`/`plotmux.scatter()` in `api.py` — see
   [4.6](#46-public-api-apipy--hist-line-scatter). Done before step 9
   — layering is only worth testing once there are at least two
   distinct chart types to overlay (e.g. line + scatter).
9. ✅ `LayerSpec` + `plotmux.layer()` + matplotlib and xy
   `render_layer` — see [4.8](#48-layering-multiple-specs-on-one-axes).
   Nesting a `LayerSpec` inside `layers` is rejected in
   `__post_init__` (see [4.8](#48-layering-multiple-specs-on-one-axes)),
   resolving that open question.
10. ✅ `export.py` format coverage for the new chart types and for
    `LayerSpec` (`export.py` itself needed no code change — it was
    already generic over any spec type via `Backend.save` — this step
    is test-only). `tests/integration/backends/{matplotlib,xy}/test_export.py`
    each parametrize over every chart type (histogram, line, scatter,
    layer) x every format that backend's `_SUPPORTED_FORMATS` declares
    (matplotlib: png/svg/pdf/jpg/jpeg; xy: those plus webp/html),
    driving the full `plotmux.hist()`/... -> `Figure.save()` ->
    `export.save()` -> `Backend.save()` pipeline end to end and
    asserting the file exists and is non-empty.
11. 🚧 A third backend (see [6.1](#61-candidate-future-backends)) once
    two chart types, colors, and layering exist on both current
    backends, to confirm the abstraction still holds under more
    surface area.

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

- Title/labels/linear-log scale now live on `BaseSpec` (see
  [4.1.1](#411-axis-labels-title-and-linearlog-scale)) and explicit
  per-mark `color` lives on each chart-type spec (see
  [4.9](#49-specifying-colors-across-backends)); both are implemented.
  Should *default* style — a color cycle for multiple series/layers
  when no `color` is set, fonts — follow the same per-spec-field
  pattern, or live on `config.py` as a global theme instead? Per-spec
  fields are simple but don't let a user set
  one palette for a whole session the way `set_backend` sets one
  backend for a whole session.
- `colors.py::parse_color` validates named colors against
  `matplotlib.colors.CSS4_COLORS`, a static table, so this works even
  when the matplotlib *backend* is unavailable — but is depending on
  `matplotlib` (even just for its color table, gated by
  `matplotlib_available()`) from `core/` an acceptable exception to
  "core never imports a plotting library" (see
  [3.1](#31-principle-separate-spec-from-render)), or does the named-
  color table need to be plotmux's own copy so `core/` has zero
  matplotlib dependency even when matplotlib isn't installed?
- **xy API verification checklist** — three assumptions about `xy`
  made in [4.8](#48-layering-multiple-specs-on-one-axes) and
  [4.9](#49-specifying-colors-across-backends), checked against the
  installed `xy` version:
  1. ✅ resolved — `xy.Chart` has no chart-composition operator (no
     `chart_a + chart_b`); `render_layer` builds the combined chart
     from `xy.chart(*marks)`, xy's generic multi-mark composer, using
     each child's already-rendered mark (see
     [4.8](#48-layering-multiple-specs-on-one-axes)).
  2. ✅ resolved — xy's native color parameter accepts a CSS color
     string, confirmed against `xy`'s own `_parse_color(css: str,
     ...)`; `rgba_to_xy()` emits `"rgba(r, g, b, a)"` with `0`-`255`
     ints for `r`/`g`/`b`.
  3. still open — does layering two children via `xy.chart(*marks)`
     give them distinct colors automatically (like matplotlib's
     shared-`Axes` default color cycle), or can two layered children
     render indistinguishably unless the caller sets an explicit
     color per child? Not blocking: `plotmux.layer()` works either
     way, this only affects the *default* look when no child sets
     `color`, which is the same unresolved default-style question as
     the first bullet above.
- `config.backend()`/`set_backend()` accept any string and only fail
  at render time via `get_backend`. Is that late failure acceptable,
  or should `set_backend`/`backend()` validate against the registry
  eagerly so a typo'd backend name fails at the call site instead of
  the next plot call?
- ✅ resolved — `LayerSpec.__post_init__` rejects nesting (a
  `LayerSpec` inside `layers` raises `ValueError`); callers must
  flatten nested layers themselves. This keeps every backend's
  `render_layer` a single flat pass over `layers` instead of forcing
  recursive dispatch for a case with no current caller need (see
  [4.8](#48-layering-multiple-specs-on-one-axes)).
- `LayerSpec` does not validate that its children make sense together
  (see [4.8](#48-layering-multiple-specs-on-one-axes)). Should
  `plotmux.layer()` at least warn — not raise — on an obvious mismatch
  such as mixing `xscale="log"` and `xscale="linear"` children once
  [4.1.1](#411-axis-labels-title-and-linearlog-scale) lands, or is
  silently taking the outer `LayerSpec`'s own scale fields (ignoring
  children's) sufficient and simpler?
- Given `xy` already covers the "interactive, HTML-exportable" niche
  (see [6.1](#61-candidate-future-backends)), is a `plotly` backend
  differentiated enough to earn its keep as backend #3, or would the
  first new backend be better spent proving something xy/matplotlib
  don't cover at all (e.g. bokeh's server/streaming model)?
