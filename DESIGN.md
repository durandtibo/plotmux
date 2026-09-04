# plotmux design

Status: implemented, current as of 2026-09-02. This document is the
**current-state architecture reference**: it describes plotmux as it
exists today, not how it got there. For the chronological log of case
studies and gap-closing rounds that produced this design, see
[`docs/docs/dev/design_history.md`](docs/docs/dev/design_history.md).

Core abstraction, nine chart specs (histogram, cdf, line, scatter,
bar, stacked bar, slope, layer, grid), five backends (matplotlib, xy,
bokeh, altair, plotly), per-mark color, common axis styling, legend
chrome (title/location/orientation), layering, grid layout, a
`plotmux.exceptions` hierarchy, export, a predefined-colors package,
lazy per-backend imports, and a third-party backend plugin mechanism
are all in place. `SlopeSpec` is registered as a standalone spec
(`plotmux.slope(...)`) only on matplotlib and bokeh, the two backends
with a native "line by slope, independent of data range" primitive;
on altair, xy, and plotly it is supported only as a `layer()` child
alongside a data-bound sibling (see
[8.1](#81-partial-or-asymmetric-backend-support)), since those three
backends need concrete endpoints, not a slope/intercept pair, and a
standalone `SlopeSpec` has no data of its own to derive endpoints
from. See [7](#7-open-questions) for what's still unresolved and
[8](#8-candidate-future-work) for what's next.

## 1. Goal

`plotmux` is a lightweight abstraction layer over Python's plotting
libraries: users write plotting code once against plotmux's unified
API and choose the rendering backend (`matplotlib`, `xy`, `bokeh`,
`altair`, `plotly`) at runtime. Swapping backends is a one-line
configuration change, and adding a new backend or chart type does not
require changing existing code.

Scope: the unified API targets a small set of generic, broadly-useful
chart types and figure-level concerns: the ones almost every plotting
task needs (histograms, empirical CDFs, line charts, scatter plots,
bar charts (plain and stacked), slope/abline annotations, layering
them together, laying them out in a grid, common axis styling,
per-mark color, export), not comprehensive coverage of every chart
type a backend can draw. Nine chart specs (histogram, cdf, line,
scatter, bar, stacked bar, slope, layer, grid, see
[4](#4-key-components)) are the current surface; a new chart type is
added when it is itself generic and broadly useful, not to chase
parity with any one backend's full plot catalog. A niche or highly
backend-specific plot is expected to stay behind the escape hatch (see
[4.3](#43-figure)) rather than becoming a new spec.

Non-goals: `plotmux` does not try to expose every feature of every
backend through the unified API, nor to cover every possible plot
type. Backend-specific power features and niche chart types remain
reachable via an escape hatch (see [4.3](#43-figure)), not by growing
the common API to the union of all backends.

## 2. Constraints from the existing codebase

- `coola` is already a dependency and its optional-dependency pattern
  (`is_*_available`, `*_available`, `raise_*_missing_error`) is
  reused as-is by `src/plotmux/utils/imports/{matplotlib,xy,bokeh,
  altair}.py`. New backends follow the same pattern instead of
  introducing a new one.
- `matplotlib`, `xy`, `bokeh`, and `altair` are declared as optional
  extras in `pyproject.toml` (`xy` is further gated to
  `python_version >= '3.11'` in its extra marker). Only `numpy` and
  `coola` are hard dependencies, so the core package (specs, registry,
  config, public API) imports cleanly with no plotting library
  installed.
- `src/plotmux/utils/range.py` (`find_range`) implements
  quantile-or-explicit axis bounds (e.g. `xmin="q0.1"`) and is reused
  by every spec that needs it rather than reimplemented per spec.
- Style conventions in place throughout: `from __future__ import
  annotations`, explicit `__all__`, Google-style docstrings with
  runnable `pycon` examples, `ruff`/`black`/`pyright` clean, tests
  split into `tests/unit/` and `tests/integration/` mirroring
  `src/plotmux/`.

## 3. Architecture

### 3.1 Principle: separate spec from render

Two layers:

1. **Chart specs**: plain, backend-agnostic frozen dataclasses
   describing *what* to plot (data + encoding + style). They never
   import a plotting library.
2. **Backends**: one class per plotting library, responsible for
   turning a spec into that library's native figure object and for
   exporting it to a file.

This mirrors the Vega-Lite/Altair split and is what makes "swap
backend in one line" true: because a spec cannot hold a matplotlib
`Axes` or an `xy.Chart`, switching backends can never leak
library-specific state back into user code.

### 3.2 Package layout

```
src/plotmux/
├── utils/
│   ├── range.py                 # find_range()
│   ├── cdf.py                    # compute_cdf_steps() -- shared step-curve
│   │                             #   vertices for bokeh/altair/xy's render_cdf
│   └── imports/                 # one module per optional backend dep
│                                 # (matplotlib.py, xy.py, bokeh.py, altair.py)
├── colors/                      # package (see 4.9.1)
│   ├── __init__.py              # re-exports parse_color, palette names
│   ├── parser.py                # parse_color()
│   ├── palette.py                # PRIMARY/SECONDARY/TERTIARY, DEFAULT_PALETTE
│   └── named.py                  # static CSS/matplotlib named-color table
├── specs/
│   ├── base.py                  # BaseSpec (title/xlabel/ylabel/xscale/yscale,
│                                 #   _normalize_color()) + _check_equal_length()
│   ├── histogram.py             # HistogramSpec
│   ├── cdf.py                    # CdfSpec
│   ├── line.py                  # LineSpec
│   ├── scatter.py                # ScatterSpec
│   ├── bar.py                     # BarSpec
│   ├── slope.py                   # SlopeSpec (gradient/intercept annotation,
│   │                             #   not data-bound; matplotlib+bokeh only)
│   ├── layer.py                  # LayerSpec (rejects nesting + empty layers)
│   └── grid.py                   # GridSpec (rejects nesting + empty cells)
├── backends/
│   ├── base.py                  # Backend ABC + resolve_renderer()/
│   │                             #   check_export_format()/make_renderer()
│   ├── registry.py              # register_backend() / get_backend() (lazy
│   │                             #   per-name import) / load_entry_point_backends()
│   │                             #   / known_backend_names()
│   ├── matplotlib/
│   │   ├── __init__.py          # registers MatplotlibBackend if available
│   │   ├── backend.py           # MatplotlibBackend
│   │   ├── style.py             # apply_common_style(ax, spec)
│   │   ├── histogram.py         # render_histogram(ax, spec) -> Axes
│   │   ├── cdf.py                 # render_cdf(ax, spec) -> Axes
│   │   ├── line.py               # render_line(ax, spec) -> Axes
│   │   ├── scatter.py            # render_scatter(ax, spec) -> Axes
│   │   ├── bar.py                 # render_bar(ax, spec) -> Axes
│   │   ├── slope.py               # render_slope(ax, spec) -> Axes, via Axes.axline
│   │   ├── layer.py              # render_layer(ax, spec) -> shared Axes
│   │   └── grid.py               # render_grid(fig, spec) -> Figure with subplots
│   ├── xy/
│   │   ├── __init__.py          # registers XyBackend if available
│   │   ├── backend.py           # XyBackend (renderers wrapped via
│   │   │                         #   backends.base.make_renderer)
│   │   ├── style.py             # rgba_to_xy(); apply_common_style(chart, spec)
│   │   ├── histogram.py         # render_histogram(spec) -> xy.Chart
│   │   ├── cdf.py                 # render_cdf(spec) -> xy.Chart
│   │   ├── line.py               # render_line(spec) -> xy.Chart
│   │   ├── scatter.py            # render_scatter(spec) -> xy.Chart
│   │   ├── bar.py                 # render_bar(spec) -> xy.Chart, via xy.bar_chart
│   │   ├── layer.py              # render_layer(spec) -> composed xy.Chart
│   │   └── grid.py               # render_grid(spec) -> XyGrid; render_grid_html()
│   │                             #   composes it to one HTML page at export time
│   │                             #   (xy has no chart-composition primitive for
│   │                             #   independent panels, so PNG/SVG/PDF/... are
│   │                             #   not supported for a grid, only "html")
│   ├── bokeh/
│   │   ├── __init__.py          # registers BokehBackend if available
│   │   ├── backend.py           # BokehBackend
│   │   ├── style.py             # rgba_to_bokeh(); apply_common_style(fig, spec)
│   │   ├── histogram.py         # render_histogram(fig, spec) -> figure
│   │   ├── cdf.py                 # render_cdf(fig, spec) -> figure
│   │   ├── line.py               # render_line(fig, spec) -> figure
│   │   ├── scatter.py            # render_scatter(fig, spec) -> figure
│   │   ├── bar.py                 # render_bar(fig, spec) -> figure, via figure.vbar
│   │   ├── slope.py               # render_slope(fig, spec) -> figure, via
│   │   │                         #   fig.add_layout(bokeh.models.Slope(...))
│   │   ├── layer.py              # render_layer(fig, spec) -> shared figure
│   │   └── grid.py               # render_grid(spec) -> bokeh gridplot layout
│   ├── altair/
│   │   ├── __init__.py          # registers AltairBackend if available
│   │   ├── backend.py           # AltairBackend (renderers wrapped via
│   │   │                         #   backends.base.make_renderer)
│   │   ├── style.py             # rgba_to_altair(); prepare_color(); apply_common_style(chart, spec)
│   │   ├── histogram.py         # render_histogram(spec) -> alt.Chart
│   │   ├── cdf.py                 # render_cdf(spec) -> alt.Chart
│   │   ├── line.py                # render_line(spec) -> alt.Chart
│   │   ├── scatter.py            # render_scatter(spec) -> alt.Chart
│   │   ├── bar.py                 # render_bar(spec) -> alt.Chart, via mark_bar()
│   │   ├── layer.py              # render_layer(spec) -> alt.LayerChart, via alt.layer(*charts)
│   │   └── grid.py               # render_grid(spec) -> alt.ConcatChart, via alt.concat(*charts)
│   └── plotly/
│       ├── __init__.py          # registers PlotlyBackend if available
│       ├── backend.py           # PlotlyBackend
│       ├── style.py             # rgba_to_plotly(); DASH_STYLE; apply_common_style(fig, spec)
│       ├── histogram.py         # render_histogram(fig, spec, row=, col=) -> go.Figure
│       ├── cdf.py                 # render_cdf(fig, spec, row=, col=) -> go.Figure
│       ├── line.py               # render_line(fig, spec, row=, col=) -> go.Figure
│       ├── scatter.py            # render_scatter(fig, spec, row=, col=) -> go.Figure
│       ├── bar.py                 # render_bar(fig, spec, row=, col=) -> go.Figure, via go.Bar
│       ├── slope.py               # render_slope(fig, spec, xrange, row=, col=) -> go.Figure;
│       │                         #   layer()-only, like altair/xy (no native abline primitive)
│       ├── layer.py              # render_layer(fig, spec, row=, col=) -> shared go.Figure
│       └── grid.py               # render_grid(spec) -> go.Figure, via plotly.subplots.make_subplots
├── figure.py                    # Figure wrapper
├── export.py                    # save(figure, path)
├── config.py                    # default backend + context manager
├── exceptions.py                # PlotmuxError hierarchy, multiply-inheriting
│                                 # from the builtin type each raise site already used
├── api.py                       # public hist(), cdf(), line(), scatter(), bar(),
│                                 #   slope(), layer(), grid()
└── testing/fixtures.py          # shared test fixtures
```

`specs/{cdf,line,scatter,bar,layer,grid}.py` and their matching
per-backend renderers are implemented across all five backends
(matplotlib, xy, bokeh, altair, plotly), with one deliberate asymmetry: xy's
grid export is HTML-only (see [4.8a](#48a-grid-layouts)). `BarSpec`
was the seventh chart type added (see [7](#7-open-questions) for the
bar chart's own history), on the strength of a bar chart being used
across every one of the (then four) backends' own plot catalogs, with no
natural encoding into an existing spec (unlike, say, a step-histogram
variant, which would just be a `HistogramSpec` option).

`SlopeSpec` was the eighth chart type added, and the first
implemented on *fewer* than all backends as a *standalone* spec,
by design (see [8.1](#81-partial-or-asymmetric-backend-support) and
[`docs/docs/dev/design_history.md`](docs/docs/dev/design_history.md)):
it is registered in `MatplotlibBackend._RENDERERS`/
`BokehBackend._RENDERERS` (and each backend's own `layer.py`, so it
can appear as a `layer()` child) directly, since matplotlib's
`Axes.axline`/bokeh's `bokeh.models.Slope` are both genuine "line by
slope, independent of data range" primitives. Requesting it
standalone on `altair`/`xy`/`plotly` raises the same `UnsupportedSpecError`
any spec with no renderer registered for a backend would (via
`resolve_renderer`, see [4.2](#42-backend)) -- it is simply not
registered in `AltairBackend._RENDERERS`/`XyBackend._RENDERERS`/
`PlotlyBackend._RENDERERS`. As a `layer()` child on those three
backends, though, `SlopeSpec` *is* supported:
`plotmux.backends.altair.layer.render_layer`/
`plotmux.backends.xy.layer.render_layer`/
`plotmux.backends.plotly.layer.render_layer` compute the x-range spanned
by its data-bound siblings (via
`plotmux.utils.slope.resolve_slope_xrange`) and hand it to a
`layer()`-only `render_slope(spec, xrange)` (registered only in each
backend's own `layer.py` dispatch table, not in the backend's
top-level `_RENDERERS`), which draws a plain two-point line between
that range's endpoints -- altair's `mark_line`/xy's `xy.line`/plotly's
`go.Scatter(mode="lines")` have no native slope primitive (plotly's own
`add_shape`/`add_hline`/`add_vline` annotations either need concrete
data-space endpoints too or only cover the horizontal/vertical special
cases), so this is the closest equivalent, and it is exact (not an
approximation) because the range comes from the actual sibling data,
not a guess. A `layer()` call with only `SlopeSpec` children (no
data-bound sibling to derive a range from) still raises
`UnsupportedSpecError` on `altair`/`xy`/`plotly`, since there is
nothing to compute a range from.
Unlike every other spec, `SlopeSpec` is not data-bound: it describes
a line by `(gradient, intercept)` rather than by `x`/`y` arrays, so it
draws without owning any data of its own and typically appears as a
`layer()` child alongside a data-bound spec (see
[4.8](#48-layering-multiple-specs-on-one-axes)) -- required, rather
than just typical, for altair/xy/plotly per the above.

The layout otherwise leaves room for one more chart type (a new
`specs/<type>.py` plus one `_RENDERERS` entry per backend) if a
similarly generic type comes up. A new backend (see
[6](#6-candidate-future-backends)) adds a new `backends/<name>/`
subpackage alongside the existing four, or, since
[3.4](#34-lazy-registration-and-third-party-plugins), can be added
entirely outside this repository via the `plotmux.backends` entry
point, with no subpackage here at all.

### 3.3 Data flow

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
backends/registry  get_backend("matplotlib") -> lazily imports
   │                 plotmux.backends.matplotlib (registers it as a
   │                 side effect, first time only) -> MatplotlibBackend
   ▼
backends/matplotlib.backend.render(spec)  ->  native matplotlib Figure
   │
   ▼
figure.py         Figure(spec, backend_name, native)
   │
   ▼
user code         fig.show() / fig.save("out.png") / fig.to_native()
```

Every public entry point (`hist`, `cdf`, `line`, `scatter`, `layer`,
`grid` in `api.py`) funnels through one shared `_render(spec, backend,
**kwargs)` helper that resolves the backend name, calls
`Backend.render`, and wraps the result in a `Figure`, so this data
flow is written once, not once per public function.

### 3.4 Lazy registration and third-party plugins

Registration is **lazy**: `plotmux/__init__.py` does *not* import any
of the four built-in backend subpackages at `import plotmux` time.
Instead, `backends/registry.py` holds `_BUILTIN_BACKEND_MODULES`, a
`{name: module path}` map, and `get_backend(name)` imports the
matching submodule on first request for that name; each subpackage's
`__init__.py` registers itself as an import-time side effect (guarded
by its own `is_*_available()` check), triggered on that first
request rather than at `import plotmux` time. This means `import
plotmux` does not pay the import cost (and underlying-library import
cost) of every installed backend regardless of which one, if any, a
given process actually uses; a process that only ever calls
`plotmux.hist(..., backend="matplotlib")` never imports `xy`,
`bokeh`, or `altair` even if all three happen to be installed
alongside matplotlib.

`plotmux/__init__.py` additionally calls
`load_entry_point_backends()` once, at import time: this is the
plug-in mechanism for a *third-party* backend to register itself
without editing plotmux's source, via a
`[project.entry-points."plotmux.backends"]` entry in the plugin
package's own `pyproject.toml`, pointing at a module that calls
`register_backend(...)` the same way a built-in backend subpackage
does. A plugin module that fails to import because its underlying
library isn't installed is silently skipped (`ImportError`); any other
exception it raises while loading is caught and turned into a
`RuntimeWarning` instead of propagating, so a broken third-party
plugin can never crash `import plotmux` for every user; it can only
fail to register itself. This is what lets [6](#6-candidate-future-backends)'s
remaining candidates (plotly, plotnine, ...) ship as independent
packages instead of requiring a PR into this repository.

## 4. Key components

### 4.1 `BaseSpec`

`BaseSpec` holds the common figure-level fields every chart type
inherits (`title`, `xlabel`, `ylabel`, `xscale`, `yscale`) so they
are defined once instead of being redeclared per chart type, and
gives `Backend.render` / the `_RENDERERS` dicts a common type to
dispatch on. It also owns two small helpers shared by concrete specs'
own `__post_init__`, so the same few lines aren't repeated in every
spec:

- `_normalize_color(name="color")`: parses a `str | tuple | None`
  color field via `parse_color` and writes the canonical RGBA value
  back in place (via `object.__setattr__`, since specs are frozen).
  Every color-carrying spec's `__post_init__` calls
  `self._normalize_color()` instead of reimplementing parse-and-write.
- `_check_equal_length(x, y)`: a module-level function (not a method,
  since not every spec has an x/y pair) that coerces `x`/`y` to
  `np.ndarray` and raises `InvalidSpecError` if their lengths differ;
  shared by `LineSpec` and `ScatterSpec`.

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
non-default field cannot follow a default one; callers already pass
them by keyword (`plotmux.hist(..., title=...)`), so this changes no
call site.

`xmin`/`xmax` are resolved through the existing `find_range` so the
quantile-string convention (`"q0.1"`) is defined once, in `utils/`,
and reused by every spec and every backend. Validation (`bins > 0`)
happens in `__post_init__`, raising `InvalidSpecError` (see
[4.2.1](#421-plotmuxexceptions)), so an invalid spec fails before any
backend is touched.

#### 4.1.1 Axis labels, title, and linear/log scale

These are figure-level concerns, not encoding channels, so they live
on `BaseSpec` and are applied the same way regardless of chart type:

```python
plotmux.hist(values, title="Latency distribution", xlabel="ms", ylabel="count")
plotmux.line(x, y, yscale="log")
```

Each backend's `render()` draws the chart-specific mark first (via its
per-type renderer, e.g. `render_histogram`), then applies these common
fields in one shared, backend-owned helper, for matplotlib,
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

Each `_RENDERERS` entry is called right after its per-type renderer
draws the mark, so a new chart type gets title/label/scale support for
free: its renderer only needs to draw the mark, not handle axis
styling. matplotlib and bokeh (both mutable, shared-object backends)
each wire `apply_common_style` at the tail of their own local
`_make_renderer` helper, once per backend rather than once per chart
type. xy and altair (both immutable-`Chart` backends) instead share
one common wrapper, `backends/base.py::make_renderer(chart_render,
style)`: it returns a `(spec, **kwargs) -> style(chart_render(spec,
**kwargs), spec)` closure, so both backends' `_RENDERERS` dicts read
as `SpecType: make_renderer(render_<type>, apply_common_style)` and
neither backend hand-writes its own near-identical wrapper (see
[4.2](#42-backend)).
One xy-specific wrinkle: `xy.Chart` is structure-immutable (see its
own `append()` docstring), so `apply_common_style` builds a *new*
`Chart`: same `kind` and existing `children` (the mark(s) already
drawn) plus an appended `xy.x_axis(label=..., type_=...)` /
`xy.y_axis(...)` pair, rather than mutating `chart` in place. Layout
(`width`/`height`/`padding`/`data`) is copied over explicitly from the
input chart; other `Chart` constructor arguments are deliberately
*not* reflected generically via `getattr`/introspection, because
several (e.g. `select`) are stored under a private attribute name
specifically because the public name collides with a same-named
`Chart` method (`Chart.select()`): a generic copy would silently
pick up the bound method instead of the stored value.

`xscale`/`yscale` default to `"linear"` rather than `None` because,
unlike title/labels, an axis always has *some* scale; there is no
meaningful "unset" state to skip, so the field is non-optional and
the backend always calls `set_xscale`/`set_yscale` (matplotlib) or
always passes `type_` (xy).

### 4.2 `Backend`

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
per spec type without upsetting static type checkers. `render` itself
is no longer abstract: it is implemented once, on `Backend`, as
`resolve_renderer(self._RENDERERS, spec, self.name)(spec, **kwargs)`,
so a concrete backend only has to define `_RENDERERS`, a
`dict[type[BaseSpec], Callable]` keyed on the spec's concrete type
(`MatplotlibBackend._RENDERERS`, `XyBackend._RENDERERS`,
`BokehBackend._RENDERERS`, `AltairBackend._RENDERERS`); the lookup-or-raise
logic itself lives in the shared `resolve_renderer()` helper in
`backends/base.py`, not duplicated per backend. Adding a new chart
type to a backend means adding one entry to that dict; it never grows
an if/elif chain and never requires touching other backends or
`Backend.render`.

Each backend also declares its own `supported_formats: ClassVar[frozenset[str]]`
and checks it in `save()` (via the shared `check_export_format()`
helper) before delegating to the native library:

| Backend      | `supported_formats`                                |
|--------------|------------------------------------------------------|
| `matplotlib` | `png`, `svg`, `pdf`, `jpg`, `jpeg`                    |
| `xy`         | `png`, `jpg`, `jpeg`, `webp`, `svg`, `pdf`, `html`    |
| `bokeh`      | `html` only; static `png`/`svg` export would additionally require a Selenium webdriver at runtime |
| `altair`     | `html`, `json`; static `png`/`svg`/`pdf` export would additionally require `vl-convert-python` |

so an unsupported format raises early with a clear message.

#### 4.2.1 `plotmux.exceptions`

Every exception `plotmux` raises is a `PlotmuxError`, in addition to
whichever standard-library exception type the raise site would
otherwise use (`ValueError`, `RuntimeError`, `NotImplementedError`):

```python
class PlotmuxError(Exception): ...


class InvalidSpecError(PlotmuxError, ValueError): ...


class InvalidColorError(PlotmuxError, ValueError): ...


class UnsupportedSpecError(PlotmuxError, NotImplementedError): ...


class UnsupportedFormatError(PlotmuxError, ValueError): ...


class ExportError(PlotmuxError, ValueError): ...


class BackendNotFoundError(PlotmuxError, RuntimeError): ...
```

Each concrete exception multiply-inherits from both `PlotmuxError` and
the matching builtin, so `except ValueError` (or `RuntimeError`/
`NotImplementedError`) at a call site keeps working exactly as
before, while new code can catch anything plotmux-specific in one
place with `except PlotmuxError`, without having to know or enumerate
which builtin type backs each individual error. These are raised by
spec validation (`__post_init__`, uniformly via `InvalidSpecError`
across every spec: histogram, cdf, line, scatter, bar, layer, grid),
color parsing, backend dispatch, and export.

### 4.3 `Figure`

Thin wrapper returned to the user: `(spec, backend_name, native)`.

- `.show()`: calls `native.show()` if the native object exposes it,
  otherwise raises `NotImplementedError`.
- `.save(path)`: delegates to `export.save`, which infers the format
  from the file suffix and calls `backend.save(native, path, fmt)`.
- `.supported_formats`: a property delegating to
  `get_backend(self.backend_name).supported_formats` (see
  [4.2](#42-backend)), so callers can check what a figure's backend
  supports before calling `.save()` instead of discovering it via a
  raised `UnsupportedFormatError`.
- `.to_native()`: returns the underlying matplotlib `Figure` /
  `xy.Chart`.

`to_native()` is the deliberate escape hatch: it keeps the common API
small without trapping users who need one backend-specific feature.

`Figure` also makes itself display automatically as the last
expression of a Jupyter cell, without every backend having to
reimplement its own rich-display wrapper: `__getattr__` forwards a
fixed, closed set of IPython/Jupyter dunder methods (`_repr_html_`,
`_repr_mimebundle_`, `_repr_svg_`, `_repr_jpeg_`) to `native`: closed
rather than forwarding arbitrary attribute access, so a typo like
`fig.sav(...)` still raises a clear `AttributeError` instead of
silently forwarding to `native`. `_repr_png_` gets its own method
instead of living in that forwarded set: it tries `native._repr_png_`
first, then falls back to a duck-typed `native.canvas.print_png` (the
shape `MatplotlibBackend` attaches to every `Figure` it builds, since
matplotlib's own `Figure` has no `_repr_png_` of its own outside
`%matplotlib inline`), without `figure.py` importing matplotlib
itself, which would break the "a backend module is only imported when
its library is installed" rule every other backend follows.

### 4.4 Backend registry

`backends/registry.py` holds a `name -> Backend` mapping
(`_REGISTRY: dict[str, Backend]`), plus `_BUILTIN_BACKEND_MODULES`, a
`name -> module path` mapping for the four built-in backends. Each
backend subpackage's `__init__.py` registers its own instance at
import time, guarded by that library's `is_*_available()` check (same
pattern as `utils/imports/matplotlib.py`); `get_backend(name)` imports
the matching built-in submodule lazily, the first time that name is
requested, rather than `plotmux/__init__.py` importing all four up
front (see [3.4](#34-lazy-registration-and-third-party-plugins)).
`load_entry_point_backends()` additionally imports every module
advertised under the `plotmux.backends` entry-point group, once, at
`import plotmux` time, registering any third-party backend the same
way. Requesting an unregistered backend raises `BackendNotFoundError`
naming the requested backend and listing the currently-registered
ones.

`known_backend_names()` computes the set of *known* backend names
without importing anything: the union of `_BUILTIN_BACKEND_MODULES`
keys, whatever `entry_points(group=ENTRY_POINT_GROUP)` currently
advertises (reading installed packages' metadata is cheap; it does
not import them), and whatever is already in `_REGISTRY`. This backs
`config.set_backend()`'s fast validation (see [4.5](#45-configpy)): a
typo'd or nonexistent backend name fails immediately, at zero import
cost, while a name that is merely *known* but not yet *registered*
(its underlying library isn't installed) only fails later, at render
time, via `get_backend`.

### 4.5 `config.py`

```python
plotmux.set_backend("matplotlib")  # process-wide default

with plotmux.backend("xy"):
    fig = plotmux.hist(values)  # scoped override
```

`set_backend`/`get_default_backend` hold a `contextvars.ContextVar[str]`
(`_DEFAULT_BACKEND`, default `"matplotlib"`), not a plain module-level
string: this gives each thread and each `asyncio` task its own value,
so `set_backend`/`backend(...)` in one thread/task never leaks into or
races with another, while still behaving like a single process-wide
default in the common single-threaded case. `backend(name)` is a
context manager that swaps it and restores the previous value on
exit, including when the block raises. `set_backend` validates the
name against `known_backend_names()` (see
[4.4](#44-backend-registry)) and raises `BackendNotFoundError`
immediately for an unknown one; `backend()` inherits the same check
since it calls `set_backend()` internally. A name that is known but
not yet *registered* (the underlying library isn't installed) still
only fails at render time, via `get_backend` — an intentional,
narrower gap, since checking registration would require the eager
import laziness was introduced to avoid (see
[3.4](#34-lazy-registration-and-third-party-plugins)).

### 4.6 Public API (`api.py`): `hist()`, `cdf()`, `line()`, `scatter()`, `bar()`, `slope()`, `layer()`, `grid()`

```python
def _render(spec: BaseSpec, backend: str | None, **kwargs: Any) -> Figure:
    r"""Resolve the backend name, render the spec, wrap the result."""
    backend_name = backend or get_default_backend()
    native = get_backend(backend_name).render(spec, **kwargs)
    return Figure(spec=spec, backend_name=backend_name, native=native)


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
    return _render(spec, backend, **kwargs)
```

`_render` factors out the three steps every public function shares
(resolve backend name, render, wrap in `Figure`); each function's own
body is only "build the matching spec from its arguments." `cdf(values,
*, nbins=None, ...)` follows `hist`'s shape almost exactly (`nbins`
in place of `bins`, `ylabel` defaulting to `"cumulative probability"`
instead of `None`, see [4.1](#41-basespec)). `line(x, y,
*, label=None, color=None, ...)`, `scatter(x, y, *, label=None,
color=None, size=None, ...)`, and `bar(x, y, *, label=None,
color=None, width=0.8, ...)` follow the same shape: build the matching
spec (`LineSpec`/`ScatterSpec`/`BarSpec`), call `_render`. All three
accept `title`/`xlabel`/`ylabel`/`xscale`/`yscale` with identical
names and defaults as `hist()`, since they map straight onto
`BaseSpec` fields shared by all specs: no per-function special-casing
needed. `size` is `ScatterSpec`-only, `width` is `BarSpec`-only, and
`nbins`/`density` are `CdfSpec`/`HistogramSpec`-only, following the
rule that fields which don't apply to every chart type live on that
chart type's own spec, not on `BaseSpec`. Specs and backends remain
directly importable for advanced use; `api.py` is only the
convenience surface most users touch.

`slope(gradient, intercept=0.0, *, label=None, color=None,
linewidth=None, linestyle="solid", ...)` builds a `SlopeSpec` and
calls `_render` like every other function here -- `_render` itself
does not know or care that only two of the five backends have a
`SlopeSpec` renderer registered; `get_backend(name).render(spec)`
raises `UnsupportedSpecError` for `altair`/`xy`/`plotly` the same way it would
for any spec/backend combination with no `_RENDERERS` entry (see
[4.2](#42-backend)), so `slope()` needed no special dispatch logic of
its own, only its own spec-construction body like `hist`/`line`/etc.

`layer(*items, title=None, xlabel=None, ylabel=None, xscale="linear",
yscale="linear", backend=None, **kwargs)` and `grid(*items, ncols=1,
title=None, backend=None, **kwargs)` are the two composition
functions (see [4.8](#48-layering-multiple-specs-on-one-axes) and
[4.8a](#48a-grid-layouts)); both accept a `Figure` in `*items` as
shorthand for its `.spec`, discarding the earlier native figure since
two independent native figures can't be merged after the fact. `grid`
deliberately does *not* accept
`xlabel`/`ylabel`/`xscale`/`yscale`/`color`: those describe a single
set of axes, and a grid panel keeps its own.

### 4.7 Export (`export.py`)

`save(figure, path)` sanitizes `path` (via `coola.utils.path.sanitize_path`),
infers the format from the file suffix (`.png`, `.svg`, `.html`, ...),
looks up the backend and, when it declares `supported_formats` (see
[4.2](#42-backend)), validates `fmt` against it before creating the
parent directory, so an unsupported-format call never leaves an empty
directory behind as a side effect, then delegates to
`backend.save(native, path, fmt)`, which re-validates the format
itself (`check_export_format`) as the authoritative check. A path with
no suffix raises in `export.save` before any backend is touched. This
path is generic over any spec type, so no `export.py` code has needed
to change as chart types were added; each addition only needed test
coverage (a chart-type x format matrix per backend).

### 4.8 Layering multiple specs on one axes

plotmux supports combining multiple specs on one axes (e.g. a line
overlaid with a scatter). This needed no new mechanism in `Backend` or
`figure.py`: it fits the existing spec/backend split as one more spec
type:

```python
@dataclass(frozen=True)
class LayerSpec(BaseSpec):
    r"""A spec that draws multiple child specs on one shared axes."""

    layers: tuple[BaseSpec, ...]

    def __post_init__(self) -> None:
        if not self.layers:
            msg = "layers must contain at least one spec"
            raise InvalidSpecError(msg)
        if any(isinstance(child, LayerSpec) for child in self.layers):
            msg = "layers must not contain a LayerSpec (nesting is not supported)"
            raise InvalidSpecError(msg)
```

Nesting (a `LayerSpec` inside `layers`) is rejected: every
`render_layer` does one flat pass over `layers`, dispatching each
child by its concrete type, so allowing a nested `LayerSpec` would
force every backend's `render_layer` to recurse for a case with no
current caller need; callers must flatten nested layers themselves.

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
    return _render(spec, backend, **kwargs)
```

Accepting `Figure` as well as bare specs lets `plotmux.layer(fig1,
fig2)` read naturally when the user already called `plotmux.line(...)`
/ `plotmux.scatter(...)` separately; only their `.spec` is reused:
the earlier native objects are discarded and everything is re-rendered
together, since two independent native figures can't be merged after
the fact in either backend. `title`/`xlabel`/`ylabel`/`xscale`/`yscale`
are exposed the same way as on `hist()`/`cdf()`/`line()`/`scatter()`,
since they describe the combined axes, not any individual child.

**Backend side: no interface change.** Each backend already dispatches
on `type(spec)` via its `_RENDERERS` dict (see [4.2](#42-backend)), so
supporting layering is one more entry, `LayerSpec -> render_layer`,
per backend, same pattern as adding any chart type:

- **matplotlib** (`backends/matplotlib/layer.py`): create one `Axes`,
  then call each child's existing `render_<type>(ax, child_spec)`
  function against that same `Axes`, in `layers` order, via a small
  `_AX_RENDERERS` dict local to `layer.py` (mirrors
  `MatplotlibBackend._RENDERERS`, restricted to the non-layer types).
  This is why `render_histogram(ax, spec)`/`render_cdf(ax, spec)`/
  `render_line(ax, spec)`/`render_scatter(ax, spec)` already take an
  `Axes` rather than creating their own figure; layering was designed
  in from the start. No extra `ax.legend()` call is needed at the end:
  each child renderer already calls `ax.legend()` when its own `label`
  is set, and matplotlib's `Axes.legend()` collects every
  currently-plotted labeled artist at call time (not just the artist
  just added), so the last labeled child's own call ends up reflecting
  the full combined legend for free.
- **xy** (`backends/xy/layer.py`): xy has no chart-composition operator
  (no `chart_a + chart_b`, unlike Altair), so each child spec is
  rendered independently via its own `render_<type>(child_spec)`, and
  only its mark children are kept (each per-type renderer returns a
  single-mark `Chart` with no axes yet; axes are added once, for the
  combined chart, by `apply_common_style`). Those marks are combined
  into one `Chart` via `xy.chart(*marks)`, xy's generic multi-mark
  composer (the same primitive `xy.line_chart`/`xy.scatter_chart`/
  `xy.histogram_chart` build on, just not fixed to one mark kind).
- **bokeh** (`backends/bokeh/layer.py`) and **altair**
  (`backends/altair/layer.py`) follow their own chart-type renderers'
  shape: bokeh renders each child onto the one shared, mutable
  `figure` (same as matplotlib's shared-`Axes` approach); altair
  renders each child to its own `alt.Chart` and composes them with
  `alt.layer(*charts)`, altair's native layering operator.

`apply_common_style` (see [4.1.1](#411-axis-labels-title-and-linearlog-scale))
is applied once to the combined result, not once per child, by each
backend's own `LayerSpec` render path, exactly as for every other spec
type, so `render_layer` itself never calls it.
`title`/`xlabel`/`ylabel`/`xscale`/`yscale` on `LayerSpec` itself
describe the combined axes, and per-child style fields (if any layer
sets its own) only affect that child's marks.

Constraints are deliberately not enforced by `LayerSpec` itself (e.g.
mixing a `HistogramSpec` with incompatible axis semantics): validating
"do these children make sense together" is a backend/domain concern,
not something `specs` can know without importing plotting-library
context, consistent with [3.1](#31-principle-separate-spec-from-render).

### 4.8a Grid layouts

`plotmux.grid()` lays out several specs as independent panels (the
backend-agnostic equivalent of matplotlib's `pyplot.subplots()`) as
opposed to `layer()`, which draws every child onto one *shared* axes.
Like `LayerSpec`, this needed no new mechanism in `Backend` or
`figure.py`, just one more spec type:

```python
@dataclass(frozen=True)
class GridSpec(BaseSpec):
    r"""A spec that lays out multiple child specs as independent panels."""

    cells: tuple[BaseSpec, ...]
    ncols: int = 1

    def __post_init__(self) -> None:
        if not self.cells:
            msg = "cells must contain at least one spec"
            raise InvalidSpecError(msg)
        if any(isinstance(child, GridSpec) for child in self.cells):
            msg = "cells must not contain a GridSpec (nesting is not supported)"
            raise InvalidSpecError(msg)
        if self.ncols <= 0:
            msg = f"ncols must be a positive integer, but received {self.ncols}"
            raise InvalidSpecError(msg)
```

Nesting is rejected for the same reason as `LayerSpec`: layout is one
flat pass over `cells`, so callers must flatten nested grids
themselves. A cell may itself be a `LayerSpec`, since layering and
gridding are independent, composable concerns (several series sharing
one panel's axes).

`GridSpec` inherits `xlabel`/`ylabel`/`xscale`/`yscale` from
`BaseSpec` but every backend's grid renderer ignores them: they have
no meaning at the grid level since each cell keeps its own axes and
style. `grid()` in `api.py` reflects this: unlike `hist`/`cdf`/`line`/
`scatter`/`layer`, it does not expose those parameters at all, only
`title` (shown once above the whole grid), `ncols`, and `backend`.

**Backend side:** one more `_RENDERERS`-style dict entry per backend,
`GridSpec -> render_grid`, following the same pattern as layering:

- **matplotlib** (`backends/matplotlib/grid.py`): creates one `Figure`
  with `ncols`-wide subplots (`len(cells)` panels, extra axes in a
  short last row turned off), then renders each cell's spec onto its
  own `Axes` via the existing per-type `render_<type>(ax, spec)`
  functions.
- **bokeh** (`backends/bokeh/grid.py`): renders each cell to its own
  `bokeh.plotting.figure`, then composes them with
  `bokeh.layouts.gridplot(..., ncols=ncols)`.
- **altair** (`backends/altair/grid.py`): renders each cell to its own
  `alt.Chart`, then composes them with `alt.concat(*charts,
  columns=ncols)`, altair's declarative grid-concatenation primitive
  (distinct from `alt.layer`, used for `LayerSpec`).
- **xy** (`backends/xy/grid.py`): xy has no chart-composition operator
  suited to independent-panel layout (`xy.facet_chart` is strictly
  *data-driven* faceting: it repeats one fixed mark composition once
  per value of a `by` data column, not a way to arrange arbitrary,
  already-built, heterogeneous charts side by side). So this backend
  does *not* render a `GridSpec` straight to an `xy.Chart` the way its
  other renderers do: `render_grid` renders and styles each cell
  independently (same as the other three backends) but returns an
  `XyGrid` (a small dataclass just holding the per-cell charts,
  `ncols`, and `title`), deferring actual layout to export time.
  `XyBackend.save` special-cases an `XyGrid` native object: each
  cell's own `Chart.to_html()` is already a complete, self-contained
  document (own `<head>`, inline script, a restrictive CSP), so cells
  can't be concatenated as HTML fragments into one document without
  one cell's script or CSP clobbering another's; instead,
  `render_grid_html` embeds each cell's document in its own sandboxed
  `<iframe srcdoc=...>` and arranges the iframes with CSS grid. This
  makes `grid(..., backend="xy")` HTML-only: `XyBackend.save` raises
  `UnsupportedFormatError` for any other format, with a message
  explaining why (no rasterization path exists for an `XyGrid`, unlike
  a bare `xy.Chart`, which still supports the full `supported_formats`
  set). This is a deliberate, permanent asymmetry between xy and the
  other three backends' grid support.

### 4.9 Specifying colors across backends

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

**Canonical input, one parser, reused everywhere**: mirrors how
`xmin`/`xmax` funnel through the single `find_range` in `utils/`
instead of every spec/backend reimplementing quantile parsing.
`colors/parser.py::parse_color` accepts the formats users already know
and that both matplotlib and xy already understand as *input*:

- a hex string, `"#rrggbb"` or `"#rrggbbaa"`
- a CSS/matplotlib named color, `"tab:blue"`, `"crimson"`, ...
  (resolved via `matplotlib.colors.to_rgba`, so this validation works
  even when the matplotlib *backend* isn't registered: `colors/parser.py`
  only calls `check_matplotlib()` and imports `to_rgba` directly, not
  a call into a `Backend`. Hex strings and RGB(A) tuples, unlike named
  colors, need no matplotlib import at all, so `parse_color` only
  requires matplotlib to be *installed* for the named-color case)
- an RGB(A) tuple of floats in `[0, 1]`, matplotlib's own convention

`parse_color` normalizes any of these to one canonical representation,
an RGBA tuple of floats in `[0, 1]`, and raises `InvalidColorError` on
anything else (out-of-range floats, unknown names, malformed hex),
so a bad color fails in spec `__post_init__` (via `BaseSpec._normalize_color`,
see [4.1](#41-basespec)), before any backend is touched, same as an
invalid `bins`.

**Canonical representation, N backend-native encoders.** Each backend
converts the normalized RGBA tuple to whatever its native call
expects, in its own `style.py` (see [4.1.1](#411-axis-labels-title-and-linearlog-scale)):

- matplotlib accepts `(r, g, b, a)` floats in `[0, 1]` directly:
  `ax.hist(..., color=spec.color)` needs no conversion once
  `spec.color` is already a `parse_color` output.
- xy's mark `color` parameter accepts a CSS color string (verified
  against `xy`'s own `_parse_color`, which resolves a CSS string via
  its native grammar), `backends/xy/style.py::rgba_to_xy(color:
  tuple[float, float, float, float]) -> str` converts the canonical
  RGBA tuple to `"rgba(r, g, b, a)"` with `r`/`g`/`b` as `0`-`255`
  ints, so the translation lives next to the backend it's for, not in
  `colors/`.
- bokeh and altair have their own equivalent converters,
  `backends/bokeh/style.py::rgba_to_bokeh` and
  `backends/altair/style.py::rgba_to_altair`, following the same
  pattern.

This keeps `colors/` matplotlib-*format*-shaped (RGBA `[0, 1]` is just
a convenient universal wire format, not a matplotlib dependency)
without making `colors/` matplotlib-*library*-dependent for every
input shape, and it means adding a color format later (e.g. HSL) only
touches `parse_color`, never a backend.

Multiple series or multiple `LayerSpec` children defaulting to
*distinct* colors when the user sets no `color` at all (a color
*cycle*, not an explicit color): matplotlib gets this for free from
its own default cycle when children share an `Axes` (see
[4.8](#48-layering-multiple-specs-on-one-axes)), but bokeh/altair/xy/
plotly do not, so `LayerSpec.__post_init__` assigns successive
`DEFAULT_PALETTE` entries to any child whose own `color` field is
`None` (`specs/layer.py::_assign_default_colors`, see
[4.9.1](#491-predefined-colors)), giving every backend matplotlib's
for-free behavior instead of four of five looking worse by omission.
A child with an explicit `color` is left untouched and does not
consume a palette slot. `GridSpec` deliberately gets no such
assignment: each cell keeps its own independent axes, so there is no
shared-axes indistinguishability problem to solve there.

#### 4.9.1 Predefined colors

```
src/plotmux/colors/
├── __init__.py   # re-exports parse_color, the predefined names/palette
├── parser.py     # parse_color()
├── palette.py    # predefined named colors + a default categorical palette
└── named.py      # static CSS/matplotlib named-color table
```

`palette.py` defines a small, fixed set of named colors (`PRIMARY`,
`SECONDARY`, `TERTIARY`) and a default categorical palette
(`DEFAULT_PALETTE`, an ordered tuple of 10 colors starting with those
three), each already a `parse_color`-normalized RGBA tuple, so callers
and backends never need to re-parse them. This is the same "canonical
input, one parser, reused everywhere" pattern as
[4.9](#49-specifying-colors-across-backends): `parse_color` stays the
only place that understands hex/named/tuple input, `palette.py` just
supplies values that already went through it (each entry is itself a
named CSS/matplotlib color, e.g. `"tab:blue"`, passed straight through
`parse_color`). `named.py` holds the static CSS/matplotlib name table
`parse_color` resolves named colors against, kept as its own module so
`parser.py` stays focused on parsing logic rather than data.

`LayerSpec.__post_init__` pulls successive entries from
`DEFAULT_PALETTE` (via `dataclasses.replace`, since specs are frozen)
for any child that sets no explicit `color`, skipping children that
already set one and children with no `color` field at all (looked up
with `getattr(child, "color", "unset")` rather than an `isinstance`
check, since `color` isn't a `BaseSpec` field and new color-carrying
spec types shouldn't need this helper updated). `palette.py` itself
stays backend-agnostic, holding RGBA tuples, not matplotlib or xy
objects; only `specs/layer.py` reads `DEFAULT_PALETTE` automatically,
and only for `LayerSpec`.

## 5. Why this shape

- **Works for any backend, not just today's four**: nothing outside a
  `backends/<name>/` subpackage may special-case a backend by name.
  `Figure`, `export.py`, `config.py`, and `api.py` only ever go
  through `Backend`'s interface (`render`, `save`, `supported_formats`)
  and the registry (`get_backend`, `register_backend`); never
  `if backend_name == "matplotlib"`. This is why adding `xy`, `bokeh`,
  and `altair` each required zero changes to any of those four
  modules, and it is the bar any future backend (plotly, ...) must
  also clear, including one added purely as a third-party plugin via
  the entry-point mechanism (see
  [3.4](#34-lazy-registration-and-third-party-plugins)), with no
  change to plotmux itself at all.
- **Extensibility without breaking existing code**: a new backend is
  a new subpackage plus one registry entry (proven four times already:
  matplotlib, xy, bokeh, altair) or, since
  [3.4](#34-lazy-registration-and-third-party-plugins), an entirely
  external package; a new chart type is a new spec plus one
  `_RENDERERS` entry per backend (proven seven times: histogram, cdf,
  line, scatter, bar, layer, grid). Neither touches the other, and common
  axis styling (title/labels/scale) is handled once per backend via
  `apply_common_style` (shared, for the two immutable-`Chart`
  backends, via `make_renderer`), not once per chart type, see
  [4.1.1](#411-axis-labels-title-and-linearlog-scale).
- **Optional dependencies stay optional, and cheap**: `utils/`,
  `specs/`, `colors/`, `figure.py`, `config.py`, `api.py`, `export.py`
  are always importable; every backend subpackage is gated behind its
  own `utils/imports/*` guard, consistent with the extras declared in
  `pyproject.toml`. Since
  [3.4](#34-lazy-registration-and-third-party-plugins), that guard
  also only runs when a backend name is actually requested, not at
  `import plotmux` time, so a process using one backend never imports
  the other four (or their underlying libraries) at all.
  `tests/unit/backends/{matplotlib,xy,bokeh,altair,plotly}/test_init.py`
  cover the "library not installed -> no registration" path.
- **Testability**: specs are plain dataclasses, cheap to unit test
  without a real plotting library installed (same style as
  `tests/unit/utils/test_range.py`). Backend rendering gets a thinner,
  separate test layer, mirroring the existing
  `tests/unit/utils/imports` vs `tests/integration/utils/imports`
  split.
- **No leaky abstraction trap**: `Figure.to_native()` means "unified
  API" doesn't have to mean "least common denominator forever."

## 6. Candidate future backends

matplotlib (static), xy (interactive HTML), bokeh (interactive,
server-callback-oriented), altair (declarative Vega-Lite), and plotly
(`plotly.graph_objects`, interactive, large existing user base and
native Jupyter/Dash support) are implemented and already anchor
several different points in the space plotmux needs to cover. plotly
turned out to diverge enough from bokeh/altair/xy to earn its keep as
backend #5 (see [3.2](#32-package-layout)): it is the only backend
besides matplotlib/bokeh with a genuine subplot-grid primitive
(`plotly.subplots.make_subplots`, used by
`plotmux.backends.plotly.grid.render_grid`) rather than composing
independently-built panels after the fact, even though (like
altair/xy) it has no native slope-by-itself primitive. It shipped as
an in-repository `backends/plotly/` subpackage rather than a pure
entry-point plugin, following the matplotlib/xy/bokeh/altair
precedent exactly (see [5](#5-why-this-shape)), since the plugin
mechanism ([3.4](#34-lazy-registration-and-third-party-plugins)) is
meant for backends maintained *outside* this repository, and there
was no reason to hold plotly to a different bar. Remaining candidate:

- **plotnine** (ggplot2-style): matches users coming from R; mostly
  static like matplotlib, so lower priority unless there is specific
  user demand.

Not scheduled; it is a `backends/<name>/` subpackage plus a
`utils/imports/<name>.py` guard plus one `pyproject.toml` extra (or an
entirely external package using the entry-point mechanism), following
the matplotlib/xy/bokeh/altair/plotly precedent exactly, see the
backend-agnostic rule in [Section 5](#5-why-this-shape). Picking one
should be driven by actual user requests, not by this list.

## 7. Open questions

- `colors/parser.py::parse_color` resolves named colors via
  `matplotlib.colors.to_rgba`, gated by `check_matplotlib()`, so this
  works even when the matplotlib *backend* is unavailable, but it
  does require matplotlib to be *installed* for the named-color case
  (hex strings and RGB(A) tuples need no matplotlib import at all).
  Is depending on `matplotlib` from `colors/`, a module outside any
  `backends/<name>/` subpackage, an acceptable exception to "non-
  backend code never imports a plotting library" (see
  [3.1](#31-principle-separate-spec-from-render)), or does named-color
  resolution need to be plotmux's own copy so `colors/` has zero
  matplotlib dependency even when matplotlib isn't installed?
- `LayerSpec` does not validate that its children make sense together
  (see [4.8](#48-layering-multiple-specs-on-one-axes)). Should
  `plotmux.layer()` at least warn (not raise) on an obvious mismatch
  such as mixing `xscale="log"` and `xscale="linear"` children, or is
  silently taking the outer `LayerSpec`'s own scale fields (ignoring
  children's) sufficient and simpler?
- Does the per-spec-field default-color-cycle pattern used by
  `LayerSpec` (see [4.9.1](#491-predefined-colors)) generalize to a
  future multi-series spec, and should other default *style* (fonts,
  etc., not just color) follow it too, or live on `config.py` instead
  so a user can set one theme for a whole session the way
  `set_backend` sets one backend for a whole session? `GridSpec` was
  deliberately left out of this resolution, so a similar question
  would still apply there if grid cells ever needed coordinated
  default colors.
- Histogram/cdf/line/scatter/bar/layer/grid were picked as "generic
  and broadly useful" (see [1. Goal](#1-goal)), but that bar isn't
  written down precisely. `BarSpec` cleared it informally (a bar chart
  is in every one of the (then four) backends' own plot catalogs, and has no
  natural encoding into an existing spec), but a box plot has a
  similarly plausible claim: should the next chart-type addition still
  be decided case by case as demand shows up, or does the project need
  an explicit, written-down checklist before adding an eighth spec?
- `BarSpec.width` (a bar width in `x` data units, matching
  matplotlib's/bokeh's own `width`) has no altair equivalent: altair's
  `render_bar` deliberately does not forward it (see
  `plotmux.backends.altair.bar`), since Vega-Lite derives a bar mark's
  rendered width from its scale rather than accepting a data-unit
  width at construction time. Is a silently-ignored `width` on that
  one backend an acceptable, permanent asymmetry (bokeh's HTML-only
  export and xy's HTML-only grid are already precedent for
  backend-specific gaps), or does this need a warning, the same
  open question as the `LayerSpec` child-compatibility one above?

## 8. Candidate future work

None of the following are scheduled; each would become a new step
once picked up.

- A sixth backend, most likely `plotnine`, evaluated per
  [6](#6-candidate-future-backends). `plotly` was the fifth,
  already implemented (see [3.2](#32-package-layout)).
- A tenth chart type (e.g. a box plot), once one clears the "generic
  and broadly useful" bar discussed in [7](#7-open-questions).
  `StackedBarSpec` was the ninth, already implemented (see
  [3.2](#32-package-layout)).
- Extending default-palette assignment (currently `LayerSpec`-only,
  see [4.9.1](#491-predefined-colors)) to any future multi-series
  spec, and deciding whether other default style belongs on
  `config.py` as a session-wide theme.
- `LayerSpec` child-compatibility warnings (e.g. mismatched
  `xscale`), if real usage shows this is a common mistake worth
  surfacing early rather than a silent axis-level override.
- Structural improvements from the external design review in
  [9](#9-proposed-improvements-external-design-review-2026-09-02):
  a declarative per-field translation table for backend renderers
  ([9.1](#91-the-per-backend-translation-table-is-duplicated-by-hand-n-x-m-times)),
  reducing `api.py`'s repeated parameter boilerplate
  ([9.2](#92-apipy-is-900-lines-of-repeated-parameter-lists-and-docstrings)),
  a queryable `Backend.capabilities()` (
  [9.3](#93-unsupported-combinations-surface-only-at-render-time-never-queryable-ahead-of-it)),
  and kwarg-typo diagnostics
  ([9.4](#94-kwargs-any-forwarded-to-the-underlying-library-is-a-silent-typo-trap)).

### 8.1 Partial or asymmetric backend support

Not every spec/field is supported identically on all five backends.
This is deliberate (see [1](#1-goal)'s non-goals) rather than an
oversight, but it means a given call's portability depends on which
backend renders it. The known asymmetries, all derived from the case
studies in
[`docs/docs/dev/design_history.md`](docs/docs/dev/design_history.md):

- **`SlopeSpec` standalone support**: matplotlib and bokeh only (native
  "line by slope" primitives); altair, xy, and plotly support it only
  as a `layer()` child alongside a data-bound sibling, since they need
  concrete endpoints to draw from (see
  [3.2](#32-package-layout)).
- **`BarSpec.width`**: ignored on altair, since Vega-Lite derives a bar
  mark's rendered width from its scale rather than accepting a
  data-unit width at construction time (see
  [7](#7-open-questions)).
- **`ScatterSpec.marker="x"`**: falls back to altair's own default
  shape rather than raising; every other marker name and every other
  backend supports the full portable set.
- **`legend_location="best"`**: a no-op on bokeh, altair, and plotly
  (none has an auto-placement location); matplotlib and xy support it
  natively.
- **Export formats**: bokeh is HTML-only (static image export needs an
  extra Selenium dependency); altair supports `html`/`json` only
  without the optional `vl-convert-python` dependency; xy's `grid()`
  output is HTML-only regardless of format requested (see
  [4.8a](#48a-grid-layouts)), since xy has no chart-composition
  primitive to rasterize independently-built panels together.

None of these are bugs to fix silently -- they are the visible edge of
each backend's own primitives, consistent with [1](#1-goal)'s
"escape hatch, not union of all backends" stance. [9.3](#93-unsupported-combinations-surface-only-at-render-time-never-queryable-ahead-of-it)
proposes making this list programmatically queryable instead of only
documented here.


## 9. Proposed improvements (external design review, 2026-09-02)

The case studies in [8](#8-candidate-future-work) drive plotmux's
*feature* growth (new specs, new fields) reactively, one bokeh example
at a time. The gaps below are different in kind: they are about the
growth *process* itself -- how each new field/spec/backend gets paid
for -- and were not surfaced by any single case study because each one
only exercises one feature end to end, not the combinatorics of adding
it everywhere. None of this contradicts [5](#5-why-this-shape); it is
about the cost of keeping that shape's promise as the matrix grows.

### 9.1 The per-backend translation table is duplicated by hand, N x M times -- partly done

Every mark-level field (`color`, `alpha`, `linewidth`, `linestyle`,
`edgecolor`, ...) is translated from its canonical form to each
backend's native call independently, in that backend's own
`render_<type>.py` (see [4.9](#49-specifying-colors-across-backends)
and [8.1](#81-partial-or-asymmetric-backend-support)). With 5
backends x 9 spec types, a new common field (the last four case
studies added `alpha`, `linewidth`/`linestyle`, `background_color`,
`ymin`/`ymax`, `legend_title`, `legend_location`,
`legend_orientation`, `edgecolor`, `fill`, `marker` -- nine fields in
four case studies) means touching on the order of 10-20 call sites by
hand, each a small, easy-to-get-subtly-wrong translation (e.g. bokeh's
`alpha` rejecting `None`, altair's `strokeDash` needing a name-to-
pixel-list table `SlopeSpec` and `LineSpec` both reach into). Nothing
enforces that a field added to one backend's renderer is added to
every other's; the only thing that currently catches an omission is
the integration test matrix (chart-type x backend x format,
[5](#5-why-this-shape)), after the fact, not before.

Proposal: factor each field's canonical-to-native translation into one
small, named function per field, living beside `rgba_to_bokeh`/
`rgba_to_altair`/`rgba_to_xy`/`rgba_to_plotly` in each backend's own
`style.py` (`STROKE_DASH`, the alpha-omit-if-None pattern, and the
`DASH_STYLE` map already are this, just not named or reused
consistently). A renderer then reads as a short, declarative list of
`(spec_field, native_kwarg, translator)` triples applied by one shared
helper, instead of a bespoke `if spec.alpha is not None: kwargs["fill_alpha"]
= spec.alpha` block repeated per mark type within a backend. This
does not remove the N x M translation work (every backend genuinely
does need its own encoding), but it turns "did every backend's every
render function pick up the new field" from a question answered by
grepping five directories into one checkable per-backend list, and
makes the *pattern* (bokeh omits `None`, altair needs a name table,
...) visible and reusable instead of rediscovered per spec type.

**Partly done (2026-09-03).** `plotmux.backends.bokeh.style` now
defines `FieldRule` (`field`/`kwarg`/`translate`/`omit_if_none`) and
`apply_fields(spec, rules, kwargs)`, plus named rules for the fields
bokeh's renderers shared (`ALPHA`, `LABEL`, `LINEWIDTH`, `LINESTYLE`,
`SIZE`, `MARKER`). Every bokeh `render_<type>.py`
(`histogram`/`bar`/`cdf`/`line`/`scatter`/`slope`/`stacked_bar`) was
migrated from its own repeated `if spec.field is not None:
kwargs["..."] = spec.field` blocks to a single
`apply_fields(spec, [...], kwargs)` call; `slope.py` also shows a
field needing its own kwarg name (`line_alpha` instead of `alpha`,
since `bokeh.models.Slope` is an annotation, not a glyph) as one extra
`FieldRule`, not a bespoke branch. This is the bokeh backend only --
altair/matplotlib/plotly/xy's `style.py` still hold their own
`rgba_to_*`/`STROKE_DASH`/`DASH_STYLE` helpers but not yet the same
`FieldRule`/`apply_fields` shape, so the N x M translation work itself
is unchanged; what changed is that bokeh's own M-sized slice of it is
now one checkable list per renderer instead of a scattered `if`
per field, and the shape is there to copy into the other four
backends' `style.py` next.

### 9.2 `api.py` is ~900 lines of repeated parameter lists and docstrings -- partly done

Every public function (`hist`, `bar`, `stacked_bar`, `cdf`, `line`,
`scatter`, `slope`, `layer`) redeclares the same seven
`BaseSpec`-level parameters (`title`, `xlabel`, `ylabel`, `xscale`,
`yscale`, `background_color`, `ymin`, `ymax`) with the same defaults,
the same type union spelled out inline four times per function
(`str | tuple[float, float, float] | tuple[float, float, float,
float] | None` appears 9 times for `color` alone), and a docstring
`Args:` block that repeats the same wording for each. This is
consistent (a real strength: no function drifts from the others in
naming or default), but it means every new `BaseSpec` field (the
seven added across the four case studies) is a ~9-site edit to
`api.py` alone, on top of the ~15-20 renderer sites in
[9.1](#91-the-per-backend-translation-table-is-duplicated-by-hand-n-x-m-times),
and a docstring reviewer has to check nine near-identical copies stay
in sync rather than one.

Proposal: extract the shared `BaseSpec`-level parameters into one
`TypedDict`/`dataclass`-backed shape (e.g. a `CommonKwargs` `TypedDict`
with matching field-level docstrings written once), and have each
public function accept `**common: Unpack[CommonKwargs]` (or, more
conservatively, keep the explicit signatures for IDE-completion's
sake but generate the repeated `Args:` docstring block instead of
hand-copying it, the way `dev/generate_versions.py` already generates
`dev/config/package_versions.json` rather than hand-maintaining it).
Either approach turns "add a `BaseSpec` field" from a 9-site manual
edit in `api.py` into a 1-site edit, without changing any call site's
signature (`plotmux.hist(..., title=...)` keeps working identically
either way) or losing the current strength of dedicated,
autocompletable keyword arguments.

Done (the conservative half): `plotmux.colors.Color` is now the one
place the `str | tuple[float, float, float] | tuple[float, float,
float, float] | None` union is spelled out -- every `color`,
`edgecolor`, and `background_color` field/parameter across `specs/`
and `api.py` (23 sites) now reads `Color` instead of repeating the
union inline. And `api.py`'s `_COMMON_STYLE_ARGS` constant holds the
`title`/`xlabel`/`ylabel`/`xscale`/`yscale`/`background_color`/
`ymin`/`ymax`/`backend` `Args:` block, word for word, once; the
`_with_common_style_args` decorator splices it into `hist`, `bar`,
`line`, `scatter`, and `slope`'s docstrings (the five functions whose
copies were identical) via `str.format`, the same "generate, don't
hand-copy" move as `dev/generate_versions.py`. `cdf` (a different
`ymin` note), `stacked_bar`/`layer` (a different `background_color`
note, no `color` to refer back to), and `grid` (none of these fields)
keep their own text since theirs already wasn't identical. Explicit
signatures are untouched, so call sites and autocompletion are
unaffected. Not done: the parameter *lists* themselves (as opposed to
their docstrings) are still redeclared per function -- the
`TypedDict`/`Unpack` half of the proposal, which would collapse the
9-site signature edit itself, remains open.

### 9.3 Unsupported combinations surface only at render time, never queryable ahead of it -- done

**Done (2026-09-04).** Added `Backend.capabilities()` (instance and
classmethod) returning a `BackendCapabilities(backend_name, spec_types,
caveats)`, plus a module-level `plotmux.backends.capabilities(name)`
convenience wrapping `get_backend(name).capabilities()`. `spec_types`
is `frozenset(cls._RENDERERS)` -- no new bookkeeping. `caveats` is a
new `Backend._CAVEATS: ClassVar[tuple[str, ...]]` (empty by default)
that each backend overrides where a known partial-support caveat
exists: altair and xy both record `SlopeSpec`-is-layer-only-support
and their own respective caveat (`BarSpec.width` ignored for altair;
`GridSpec` export HTML-only for xy), and plotly records the
`SlopeSpec` caveat. matplotlib and bokeh have none. This is purely
additive and read-only -- it does not change any render-time or
export-time behavior -- and is covered by tests per backend (see
`tests/unit/backends/*/test_backend.py::test_*_backend_capabilities`
and `tests/unit/backends/test_base.py`/`test_registry.py`).

`resolve_renderer` (see [4.2](#42-backend)) raises
`UnsupportedSpecError` the moment an unsupported spec/backend
combination is actually rendered, and `Figure.supported_formats` (see
[4.3](#43-figure)) lets a caller check export-format support ahead of
`.save()` -- but there is no equivalent for spec-type or field-level
support. A caller cannot ask "does this backend support `SlopeSpec`
standalone?" or "does `BarSpec.width` do anything on altair?" (see
[7](#7-open-questions)'s last bullet) without either reading this
document or triggering the failure. This matters more as the matrix
grows: `SlopeSpec` is backend-standalone/layer-only-supported
per-backend, `BarSpec.width` is silently ignored on one backend,
xy's grid export is HTML-only, bokeh has no static image export --
four different flavors of "partial support," each currently
discoverable only by hitting it or reading DESIGN.md.

Proposal: a small `Backend.capabilities()` (or a module-level
`plotmux.backends.capabilities(backend_name)`) returning, at minimum,
the set of spec types with a registered top-level renderer (already
computable from `_RENDERERS.keys()` with no new bookkeeping) plus a
short, explicit list of the known partial-support caveats that
`_RENDERERS.keys()` alone can't express (layer-only `SlopeSpec`
support, ignored `BarSpec.width`, HTML-only grid/export). This is
strictly additive -- it does not change render-time behavior or any
existing error -- and gives library authors building on top of
plotmux (or a user picking a backend for a specific chart) a
programmatic answer instead of a DESIGN.md search.

### 9.4 `**kwargs: Any` forwarded to the underlying library is a silent typo trap

Every renderer and every public API function accepts `**kwargs: Any`
and forwards it to the underlying plotting call (see
[4.6](#46-public-api-apipy-hist-cdf-line-scatter-bar-slope-layer-grid)).
This is the right escape hatch for a real backend-specific argument,
but it also means a typo'd kwarg intended for one of plotmux's own
named parameters (e.g. `plotmux.line(x, y, colour="red")`, a common
British-spelling slip) is silently absorbed and forwarded instead of
raising immediately: the failure, if any, happens deep inside
matplotlib/bokeh/altair/plotly/xy with a traceback that does not
mention plotmux at all, and on some backends a stray kwarg the
underlying call happens to also accept silently changes behavior
instead of erroring.

Proposal: no change to the escape hatch's reach (it should keep
forwarding anything not recognized), but each backend's renderer could
cheaply check forwarded kwargs against the underlying call's own
accepted parameter names via `inspect.signature` before forwarding,
turning an unrecognized kwarg into a clear `InvalidSpecError` naming
the closest match (`"colour" -> did you mean "color"?`) instead of a
deep, confusing traceback. Low priority relative to
[9.1](#91-the-per-backend-translation-table-is-duplicated-by-hand-n-x-m-times)-[9.3](#93-unsupported-combinations-surface-only-at-render-time-never-queryable-ahead-of-it),
since it is a diagnostics improvement, not a correctness or
extensibility one, but cheap once `inspect.signature` is memoized per
underlying callable.

### 9.5 DESIGN.md itself is becoming two documents in one -- done

**Done (2026-09-02).** DESIGN.md used to mix two different kinds of
content: the current-state architecture reference ([1](#1-goal)-[6](#6-candidate-future-backends))
a new contributor needs to read once, and a chronological log of case
studies, closed gaps, and "nothing carried over from 8.x" bookkeeping,
valuable as a *history* of why each field exists but not something a
reader needs to re-derive every time. The status paragraph at the top
of the file had itself grown into a dense, run-on changelog that was
hard to skim precisely because it was trying to stay a single accurate
sentence-per-fact across nine cumulative rounds of edits.

The case-study log and the old status paragraph's history were split
out into [`docs/docs/dev/design_history.md`](docs/docs/dev/design_history.md),
leaving DESIGN.md as the current-state reference plus
[7](#7-open-questions)/[8](#8-candidate-future-work) (the *live*,
forward-looking lists) and a short [8.1](#81-partial-or-asymmetric-backend-support)
summary of the asymmetries those case studies produced, with the full
narrative linked from there rather than inlined.

None of 9.1-9.4 are scheduled; each is additive/refactor-only and
would become a new step once picked up, following the same convention
as [8](#8-candidate-future-work).
