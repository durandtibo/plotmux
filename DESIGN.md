# plotmux design

Status: implemented. Core abstraction, eight chart specs (histogram,
cdf, line, scatter, bar, slope, layer, grid), five backends
(matplotlib, xy, bokeh, altair, plotly), per-mark color, common axis styling,
layering, grid layout, a `plotmux.exceptions` hierarchy, export, a
predefined-colors package, lazy per-backend imports, and a
third-party backend plugin mechanism are all in place. `SlopeSpec` is
registered as a standalone spec (`plotmux.slope(...)`) only on
matplotlib and bokeh, the two backends with a native "line by slope,
independent of data range" primitive; on altair, xy, and plotly it is
supported only as a `layer()` child alongside a data-bound sibling
(see [8.1](#81-case-study-reproducing-bokehs-slope-example)), since
those three backends need concrete endpoints, not a slope/intercept
pair, and a standalone `SlopeSpec` has no data of its own to derive
endpoints from. `plotmux.slope(...)`/a slope-only `layer()` still
raise `UnsupportedSpecError` on those three backends. All of
[8.1](#81-case-study-reproducing-bokehs-slope-example)'s gaps (per-mark
alpha, separate marker edge color, `LineSpec`
`linewidth`/`linestyle`, figure background color, explicit `ymin`/
`ymax` axis bounds, and altair/xy support for `SlopeSpec` as a layer
child) are now closed; bokeh's own slope example is reproducible,
unchanged, on all five backends (modulo the standalone-vs-layered
`SlopeSpec` distinction on altair/xy/plotly noted above). A fifth
backend, plotly, has since been added (see
[3.2](#32-package-layout)), following the same `layer()`-only
treatment for `SlopeSpec` as altair/xy, for the same reason: no
native "line by slope, independent of data range" primitive (see
`plotmux.backends.plotly.slope`). Checked against bokeh's own legend
example (see
[8.2](#82-case-study-reproducing-bokehs-legend-example)): mostly
reproducible unchanged (auto-generated legends from `label`, a
scatter+line pair sharing one label merging into one legend entry,
dashed-line styling, a two-panel grid), but two gaps remain, not
yet closed: a legend title distinct from the figure title, and
scatter marker shape (e.g. square vs. circle) -- a claimed
"hollow-vs-filled fill control via `edgecolor`" close from the first
pass through 8.2 turned out to be bokeh-only behavior, not a real
cross-backend fix, and was corrected. Checked against bokeh's own log
plot example next (see
[8.3](#83-case-study-reproducing-bokehs-log-plot-example)): mostly
reproducible unchanged (log y-axis with explicit bounds, figure
background color, labeled dashed/dotted lines, line+scatter legend
merges), but three more gaps remain, not yet closed: explicit x-axis
bounds (`xmin`/`xmax` at the `BaseSpec` level, distinct from
`HistogramSpec`/`CdfSpec`'s existing quantile-capable `xmin`/`xmax`),
legend position, and a portable hollow (no-fill) marker. Checked
against bokeh's own stacked bar example next (see
[8.4](#84-case-study-reproducing-bokehs-stacked-bar-example)): the
first case study *not* close to reproducible -- no stacking mechanism
exists at all (`layer()`'s `BarSpec` support overlaps bars rather than
stacking them), `BarSpec`'s categorical (string) x-axis support is
inconsistent across backends (works on matplotlib/plotly, broken on
bokeh and altair, unverified on xy), and legend orientation is a third
missing legend-chrome field alongside `legend_title`/`legend_location`;
hover tooltips and fine-grained chrome cosmetics are deliberately left
as escape-hatch, non-goal territory rather than gaps. See
[7](#7-open-questions) for what's still unresolved and
[8](#8-candidate-future-work) for what's next.
Date: 2026-09-02.

## 1. Goal

`plotmux` is a lightweight abstraction layer over Python's plotting
libraries: users write plotting code once against plotmux's unified
API and choose the rendering backend (`matplotlib`, `xy`, `bokeh`,
`altair`) at runtime. Swapping backends is a one-line configuration
change, and adding a new backend or chart type does not require
changing existing code.

Scope: the unified API targets a small set of generic, broadly-useful
chart types and figure-level concerns: the ones almost every plotting
task needs (histograms, empirical CDFs, line charts, scatter plots,
bar charts, layering them together, laying them out in a grid, common
axis styling, per-mark color, export), not comprehensive coverage of
every chart type a backend can draw. Seven chart specs (histogram,
cdf, line, scatter, bar, layer, grid, see
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
by design (see [8.1](#81-case-study-reproducing-bokehs-slope-example)):
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
- An eighth chart type (e.g. a box plot), once one clears the "generic
  and broadly useful" bar discussed in [7](#7-open-questions). `BarSpec`
  was the seventh, already implemented (see [3.2](#32-package-layout)).
- Extending default-palette assignment (currently `LayerSpec`-only,
  see [4.9.1](#491-predefined-colors)) to any future multi-series
  spec, and deciding whether other default style belongs on
  `config.py` as a session-wide theme.
- `LayerSpec` child-compatibility warnings (e.g. mismatched
  `xscale`), if real usage shows this is a common mistake worth
  surfacing early rather than a silent axis-level override.
- Nothing carried over from [8.1](#81-case-study-reproducing-bokehs-slope-example):
  every gap it identified (per-mark `alpha`, a separate marker edge
  color, `linewidth`/`linestyle` on `LineSpec`, a figure background
  color, explicit `ymin`/`ymax` axis bounds, and altair/xy support for
  `SlopeSpec` as a `layer()` child) is now closed; see 8.1 for what
  each one turned into.
- A `BaseSpec`-level `legend_title` field and a `ScatterSpec.marker`
  shape field, per
  [8.2](#82-case-study-reproducing-bokehs-legend-example): the two
  gaps found reproducing bokeh's legend example. Not yet closed.
- A `BaseSpec`-level `xmin`/`xmax` pair, a `BaseSpec`-level
  `legend_location` field (to ship together with `legend_title`
  above), and a tri-state `ScatterSpec.fill` field, per
  [8.3](#83-case-study-reproducing-bokehs-log-plot-example): the three
  gaps found reproducing bokeh's log plot example. Not yet closed.
- A new `StackedBarSpec` chart type, portable categorical (string)
  `x`-axis support for `BarSpec` (currently broken on bokeh, broken on
  altair, unverified on xy), and a `BaseSpec`-level
  `legend_orientation` field (to ship together with `legend_title`/
  `legend_location` above), per
  [8.4](#84-case-study-reproducing-bokehs-stacked-bar-example): the
  gaps found reproducing bokeh's stacked bar example. The most
  significant of the four case studies so far -- stacking needs a new
  spec type, not just a new field. Not yet closed.

### 8.1 Case study: reproducing bokeh's slope example

Checked against
[bokeh's `slope` annotation example](https://docs.bokeh.org/en/latest/docs/examples/basic/annotations/slope.html)
(scatter markers with a separate yellow fill / black edge, drawn with
`alpha=0.8`, plus a dashed blue reference line of gradient 2 and
y-intercept 10 at `line_width=4`, on a figure with a light-gray
background and `y_range.start = 0`) to see whether it is reproducible
through plotmux's unified API, unchanged, on all five backends. It
**is**, now, on matplotlib and bokeh outright; on altair, xy, and
plotly with one caveat (`SlopeSpec` needs a data-bound `layer()`
sibling to derive endpoints from -- see below), unavoidable given
those three backends' own primitives. Every gap identified by this
case study is closed:

- **Slope/abline annotation.** `specs/slope.py::SlopeSpec(gradient,
  intercept=0.0, color=None, linewidth=None, linestyle="solid",
  alpha=None)` (see [3.2](#32-package-layout)). Standalone
  (`plotmux.slope(...)`), it is matplotlib (`Axes.axline`) and bokeh
  (`fig.add_layout(bokeh.models.Slope(...))`) only, each with a native
  "line by slope, independent of data range" primitive matched almost
  one-to-one by `SlopeSpec`'s fields. altair and xy have neither: a
  standalone `SlopeSpec` has no data of its own to derive concrete
  endpoints from, and drawing between two arbitrary far-apart points
  would blow out altair's own default autoscale (xy has the same
  problem, plus no way to read back whatever range it picked). As a
  `layer()` child on those two backends, though, `SlopeSpec` *is*
  supported: `plotmux.backends.altair.layer.render_layer`/
  `plotmux.backends.xy.layer.render_layer` compute the x-range spanned
  by the `SlopeSpec`'s data-bound siblings
  (`plotmux.utils.slope.resolve_slope_xrange`, reading each sibling's
  `x` array, or a `HistogramSpec`/`CdfSpec`'s `find_range`-resolved
  bound) and pass it to a `layer()`-only
  `render_slope(spec, xrange)` (registered in each backend's own
  `layer.py`, not the backend's top-level `_RENDERERS`), which draws a
  plain two-point line spanning exactly that range -- exact, not an
  approximation, since the range comes from the real sibling data. A
  `layer()` call with no data-bound sibling (e.g. two `SlopeSpec`s
  alone) still raises `UnsupportedSpecError` on altair/xy, since there
  is nothing to derive a range from; this is the one respect in which
  `SlopeSpec` support is narrower on altair/xy than on
  matplotlib/bokeh, an unavoidable consequence of those two backends
  having no slope-by-itself primitive at all, not a remaining gap.
- **Separate marker fill/edge color.** `ScatterSpec.edgecolor`, an
  optional second color field normalized through the same
  `_normalize_color` machinery as `color` (see
  [4.9](#49-specifying-colors-across-backends)); `None` (the default)
  uses `color` for the edge too, so every existing single-color
  `ScatterSpec` renders unchanged. matplotlib: `Axes.scatter`'s
  `edgecolors`; bokeh: `figure.scatter`'s `line_color`, kept separate
  from `fill_color` (both used to be set to the same `color`); altair:
  `mark_point(filled=True, stroke=...)` (a constant mark property, not
  a field-based encoding -- altair has no legend channel for a mark's
  stroke, matching every other backend's edge color never getting its
  own legend entry either); xy: `xy.scatter`'s `stroke`/`stroke_width`.
- **`alpha`.** An `alpha: float | None` field on every color-carrying
  spec (`HistogramSpec`, `CdfSpec`, `LineSpec`, `ScatterSpec`,
  `BarSpec`, `SlopeSpec`) -- placed per spec rather than on
  `BaseSpec`, mirroring how `color` itself is placed per spec (see
  [4.9](#49-specifying-colors-across-backends)), since `alpha` is a
  mark-level concern that has no meaning on `LayerSpec`/`GridSpec`.
  matplotlib: `alpha` passthrough (`None` is matplotlib's own "fully
  opaque" default, so it needs no special-casing); bokeh: each
  glyph's `alpha` (sets both `fill_alpha`/`line_alpha`) -- unlike
  matplotlib, bokeh's `alpha` property rejects `None` outright, so it
  is only added to the call when explicitly set (same pattern
  `SlopeSpec.linewidth` already used, see
  `plotmux.backends.bokeh.slope`); altair: `opacity`; xy: `opacity`.
- **`LineSpec` line width and dash style.** The same
  `linewidth: float | None` / `linestyle: Literal["solid", "dashed",
  "dotted", "dashdot"]` fields `SlopeSpec` already had, added to
  `LineSpec` too, translated per backend the same way `xscale`/
  `yscale` are: matplotlib `linewidth`/`linestyle` passthrough; bokeh
  `line_width`/`line_dash`; altair `strokeWidth`/`strokeDash` (a
  `STROKE_DASH` name-to-pixel-list map in
  `plotmux.backends.altair.style`, shared with `SlopeSpec`'s own
  altair renderer); xy `width`/`dash` (`xy.line` accepts the same
  matplotlib-style dash names directly, no translation table needed).
- **Figure background color.** `BaseSpec.background_color`, a
  `BaseSpec`-level, figure-wide field (like `title`) rather than
  per-mark, applied once in each backend's `apply_common_style`
  alongside title/labels/scale/`ymin`/`ymax`: matplotlib
  `Axes.set_facecolor`; bokeh `figure.background_fill_color`; altair
  `Chart.properties(background=...)`; xy a `style={"backgroundColor":
  ...}` entry on the `Chart` (xy's CSS-style-dict escape hatch, the
  closest xy has to a background-color constructor argument).
- **Explicit y-axis bounds.** `BaseSpec.ymin`/`ymax`: unlike
  `HistogramSpec.xmin`/`xmax` (`float | str | None`, resolved via
  `find_range`'s quantile-or-explicit convention, see
  [4.1](#41-basespec)), these are `float | None` only -- an explicit
  value, no quantile-string form -- since they are figure-level (every
  chart type has a y-axis; not every chart type has one data array to
  resolve a quantile against the way `HistogramSpec`/`CdfSpec` do).
  Applied post-hoc in `apply_common_style`, after the mark is drawn:
  matplotlib `Axes.set_ylim`; bokeh `figure.y_range.start`/`.end`
  (pinned individually on the default auto-fitting `DataRange1d`, so
  setting just one bound leaves the other autoscaled -- this is also
  what makes bokeh's `CdfSpec` renderer's own hardcoded `y_range =
  Range1d(0, 1)`, set before `apply_common_style` runs, correctly
  overridable by an explicit `ymin`/`ymax`); altair
  `alt.Scale(domainMin=..., domainMax=...)`; xy `xy.y_axis(domain=
  (ymin, ymax))` -- xy's `domain` takes both bounds together, no
  partial-bound form, so (unlike matplotlib/bokeh) only both explicit
  bounds set together are forwarded; either alone is left autoscaled.

matplotlib and bokeh reproduce the bokeh slope example exactly,
unchanged, via one `layer()` call combining a styled `ScatterSpec` and
`SlopeSpec`. altair, xy, and plotly reproduce it the same way, with the
same call -- the only difference is architectural, not user-visible:
their `SlopeSpec` support depends on the `ScatterSpec` sibling being in
the same `layer()` call to supply a range, which the bokeh example's own
structure (a scatter plus a reference line, layered) already satisfies.

### 8.2 Case study: reproducing bokeh's legend example

Checked against
[bokeh's `legend` annotation example](https://docs.bokeh.org/en/latest/docs/examples/basic/annotations/legend.html)
(two side-by-side figures in a `gridplot`: the left one three labeled
scatter series in default/orange/green; the right one a labeled
scatter+line pair sharing the label `"sin(x)"` -- meant to merge into
one legend entry -- plus a dashed orange line and a hollow green
square marker paired with a green line, each figure's legend given its
own title, `"Markers"`/`"Lines"`) to see whether it is reproducible
through plotmux's unified API, unchanged, on all five backends. Most
of it already is:

- **Auto-generated legends from `label`.** Every color-carrying spec's
  `label` field (see e.g. [4.9](#49-specifying-colors-across-backends))
  already maps onto bokeh's `legend_label`, matplotlib's
  `ax.legend()`-collected artist label, altair's `label:N` color
  encoding, and plotly's `showlegend=True` -- no gap.
- **A scatter and a line sharing one label merging into a single
  legend entry.** Already correct on every backend once both children
  are drawn via one `layer()` call: matplotlib's `Axes.legend()`
  dedupes by artist label the same way bokeh's own `legend_label`
  matching does; altair's shared `label:N` encoding and plotly's
  shared `name` behave the same way -- no gap, no extra mechanism
  needed.
- **Dashed line, line width.** Already closed by
  [8.1](#81-case-study-reproducing-bokehs-slope-example)'s
  `LineSpec.linewidth`/`linestyle`.
- **Hollow (no-fill) marker via `ScatterSpec.edgecolor`.** Partially
  wrong when first checked here: `edgecolor` (see
  [8.1](#81-case-study-reproducing-bokehs-slope-example)) only adds a
  *second*, separate edge color on top of whatever fills the marker --
  it does not make the fill transparent. `spec.color=None` +
  `edgecolor=<green>` happens to *look* hollow on bokeh only, because
  bokeh's own `fill_color=None` (what `color=None` forwards to, see
  `plotmux.backends.bokeh.scatter.render_scatter`) is bokeh's native
  "transparent fill" value; on matplotlib/altair/plotly/xy, `color=None`
  instead falls back to that library's own default *opaque* fill, so
  the same spec renders filled everywhere but bokeh. This is folded
  into the "no-fill marker" gap identified in
  [8.3](#83-case-study-reproducing-bokehs-log-plot-example), not a
  closed item.
- **Two figures side by side.** Already `plotmux.grid(fig1_spec,
  fig2_spec, ncols=2)` (see [4.8a](#48a-grid-layouts)).

Two gaps remain, both new (not raised by
[8.1](#81-case-study-reproducing-bokehs-slope-example)):

- **Legend title.** Bokeh's `p.legend.title = "Markers"` sets a
  heading on the legend box itself, independent of the figure title.
  plotmux has no equivalent field anywhere: `BaseSpec` has `title`
  (the figure/axes title) but nothing for the legend specifically, so
  there is no way to reproduce `p1.legend.title = 'Markers'`/
  `p2.legend.title = 'Lines'` today. Candidate fix: a
  `BaseSpec`-level `legend_title: str | None` field (figure-level,
  like `title`/`background_color`, since a legend belongs to the axes
  as a whole, not to any one mark), applied once in each backend's
  `apply_common_style`: matplotlib `ax.legend(title=...)` (folds into
  the existing `ax.legend()` call rather than a second one); bokeh
  `fig.legend.title = ...` (bokeh already auto-creates `fig.legend`
  once any glyph carries a `legend_label`, so this only needs setting
  after the marks are drawn, mirroring how `ymin`/`ymax` are set
  post-hoc); altair `alt.Legend(title=...)` in place of the current
  hardcoded `legend=alt.Legend(title=None)` (see
  `plotmux.backends.altair.style`); plotly `fig.update_layout(
  legend_title_text=...)`; xy would need its own equivalent checked
  against its legend API. `GridSpec`/`LayerSpec` themselves need no
  change: `legend_title` is a `BaseSpec` field like `title`, so a
  `layer()` call already exposes it the same way `title` is exposed
  today.
- **Marker shape.** Bokeh's `marker="square"` (vs. the implicit
  default circle) has no `ScatterSpec` equivalent: `ScatterSpec` (see
  [4.9](#49-specifying-colors-across-backends)) has `color`, `size`,
  `edgecolor`, and `alpha`, but no shape field, so every plotmux
  scatter series renders as whatever each backend's own default marker
  shape is (a circle on matplotlib/bokeh/altair/xy/plotly), with no
  way to request a square, triangle, cross, etc., and so no way to
  reproduce this example's hollow green square series unchanged.
  Candidate fix: `ScatterSpec.marker: Literal["circle", "square",
  "triangle", "diamond", "cross", "x"] | None = None` (a small,
  backend-portable set rather than passing through each backend's full
  native marker vocabulary, mirroring how `LineSpec.linestyle` exposes
  four portable names rather than every backend's native dash
  vocabulary), translated per backend: matplotlib `Axes.scatter`'s
  `marker=` (`"o"`/`"s"`/`"^"`/`"D"`/`"+"`/`"x"`); bokeh
  `figure.scatter`'s `marker=` (accepts `"circle"`/`"square"`/
  `"triangle"`/`"diamond"`/`"cross"`/`"x"` directly); altair
  `mark_point(shape=...)` (`"circle"`/`"square"`/`"triangle-up"`/
  `"diamond"`/`"cross"`, no native `"x"` -- the one likely
  per-backend asymmetry, same pattern as
  `BarSpec.width`'s altair gap, see
  [7](#7-open-questions)); plotly `go.Scatter(marker_symbol=...)`
  (`"circle"`/`"square"`/`"triangle-up"`/`"diamond"`/`"cross"`/`"x"`);
  xy would need its own equivalent checked against its scatter mark
  API. A translation table per backend (`MARKER_STYLE`, mirroring
  altair's existing `STROKE_DASH` table in
  `plotmux.backends.altair.style`) is the natural shape for this,
  same pattern as `linestyle`.

Neither gap is scheduled (see [8](#8-candidate-future-work)); both are
small, additive `BaseSpec`/`ScatterSpec` fields following precedent
already established by [8.1](#81-case-study-reproducing-bokehs-slope-example),
not a new mechanism.

### 8.3 Case study: reproducing bokeh's log plot example

Checked against
[bokeh's `logplot` annotation example](https://docs.bokeh.org/en/latest/docs/examples/basic/annotations/logplot.html)
(one figure, log y-axis spanning `0.001` to `10**22`, explicit
`x_range=(0, 5)`, a light-gray figure background, six labeled `y=...`
curves -- most drawn as a plain line, two paired with a scatter on the
same data, one scatter left hollow (`fill_color=None`) -- using dashed,
dotted, and dotdash line styles, a legend positioned `top_left`) to see
whether it is reproducible through plotmux's unified API, unchanged, on
all five backends. Most of it already is:

- **Log y-axis, explicit y bounds spanning many orders of magnitude,
  figure background color.** Already `yscale="log"`, `ymin=0.001`,
  `ymax=10.0**22`, `background_color="#fafafa"` -- all closed by
  [8.1](#81-case-study-reproducing-bokehs-slope-example) (see
  `BaseSpec.yscale`/`ymin`/`ymax`/`background_color`).
- **Labeled lines and line+scatter pairs sharing one legend entry,
  dashed/dotted line styles, per-line color and width.** Already
  `LineSpec.label`/`color`/`linewidth`/`linestyle` plus a `layer()`
  call per curve that needs both a line and a scatter on the same
  data, same as [8.2](#82-case-study-reproducing-bokehs-legend-example)'s
  scatter+line merge -- no gap.

Three gaps, none raised by
[8.1](#81-case-study-reproducing-bokehs-slope-example)/[8.2](#82-case-study-reproducing-bokehs-legend-example):

- **Explicit x-axis bounds.** Bokeh's `x_range=(0, 5)` has no plotmux
  equivalent: `BaseSpec` has `ymin`/`ymax` (see
  [8.1](#81-case-study-reproducing-bokehs-slope-example)) but no
  `xmin`/`xmax` counterpart at the same figure level -- `xmin`/`xmax`
  exist today only on `HistogramSpec`/`CdfSpec`, resolved through
  `find_range`'s quantile-or-explicit convention against that spec's
  own single data array (see [4.1](#41-basespec)), which is a
  different feature (a data-driven bound) from a plain axis-range
  override that applies regardless of chart type. Candidate fix: a
  `BaseSpec`-level `xmin: float | None`/`xmax: float | None` pair,
  explicit-value-only like `ymin`/`ymax` (not the quantile-string
  form), applied post-hoc in each backend's `apply_common_style`
  alongside `ymin`/`ymax`: matplotlib `Axes.set_xlim`; bokeh
  `figure.x_range.start`/`.end`; altair
  `alt.Scale(domainMin=..., domainMax=...)` on the x encoding; plotly
  `fig.update_xaxes(range=[xmin, xmax])`; xy `xy.x_axis(domain=(xmin,
  xmax))` (xy's `domain` takes both bounds together, same "only both
  set together are forwarded" caveat `ymin`/`ymax` already documents
  for xy). This would sit alongside `HistogramSpec.xmin`/`CdfSpec.xmin`
  without replacing them -- those two remain quantile-capable and
  data-scoped; the new field is a plain figure-level override open to
  every chart type, the `xmin`/`xmax` analogue of `ymin`/`ymax`.
- **Legend position.** Bokeh's `p.legend.location = "top_left"` has no
  plotmux equivalent, the same shape of gap as
  [8.2](#82-case-study-reproducing-bokehs-legend-example)'s missing
  `legend_title`: `BaseSpec` has nothing legend-specific at all today.
  Candidate fix: a `BaseSpec`-level `legend_location: Literal["best",
  "top_left", "top_right", "bottom_left", "bottom_right", ...] | None
  = None` field, naturally proposed *alongside* `legend_title` as one
  `legend_title`/`legend_location` pair rather than two unrelated
  additions, since both are set together in the bokeh original
  (`p.legend.title`/`p.legend.location`) and both apply post-hoc in the
  same `apply_common_style` step: matplotlib `ax.legend(loc=...)`
  (matplotlib's own location strings, e.g. `"upper left"`, need a small
  name-mapping table since bokeh spells them
  `"top_left"`/plotmux would too); bokeh `fig.legend.location = ...`
  (bokeh's own vocabulary directly, no translation needed since this
  candidate's names were chosen to match bokeh's); altair
  `alt.Legend(orient=...)` (altair's `orient` only supports the
  outer-edge positions -- `"top"`, `"bottom"`, `"left"`, `"right"`, plus
  the four corners -- not an arbitrary inside-plot corner the way
  matplotlib's `loc` does, likely another small, permanent per-backend
  asymmetry, same pattern as the marker-shape gap's altair note in
  [8.2](#82-case-study-reproducing-bokehs-legend-example)); plotly
  `fig.update_layout(legend=dict(x=..., y=...))` (plotly has no named
  corner enum, only `x`/`y` fractional coordinates, so this candidate's
  name set would need a name-to-`(x, y)` table); xy would need its own
  equivalent checked against its legend API.
- **Hollow (no-fill) marker as a portable concept.** Distinct from the
  marker-*shape* gap in
  [8.2](#82-case-study-reproducing-bokehs-legend-example): even with a
  circular marker, this example's `p.scatter(x, x**2, fill_color=None,
  line_color="olivedrab")` has no reliable plotmux equivalent today
  because `ScatterSpec.color` has no "explicitly transparent" value
  distinct from "unset, use the backend default" -- `color=None` means
  the latter, and as the correction above notes, only bokeh's own
  default for an unset fill happens to be transparent; every other
  backend's default fill is opaque, so the same spec would render
  filled markers on matplotlib/altair/plotly/xy and hollow ones only on
  bokeh. Candidate fix: a tri-state `ScatterSpec.fill: bool | None =
  None` (`None`/`True` = filled, using `color`, today's behavior;
  `False` = no fill, drawing only the `edgecolor`/`color` outline),
  translated per backend: matplotlib `Axes.scatter(facecolors="none")`
  when `fill is False`; bokeh `fill_color=None` (today's accidental
  bokeh-only path becomes the explicit, intentional one); altair
  `mark_point(filled=False)`; plotly `go.Scatter(marker_color=
  "rgba(0,0,0,0)")` with the outline drawn via `marker.line` (already
  wired for `edgecolor`, see [4.9](#49-specifying-colors-across-backends));
  xy would need its own equivalent checked against its scatter mark
  API (likely `color=None` combined with a nonzero `stroke_width`,
  verified rather than assumed, per xy's own "structure-immutable
  `Chart`" notes in [4.1.1](#411-axis-labels-title-and-linearlog-scale)).

None of these three are scheduled (see [8](#8-candidate-future-work));
all three are small, additive `BaseSpec`/`ScatterSpec` fields following
the same precedent as
[8.1](#81-case-study-reproducing-bokehs-slope-example)/[8.2](#82-case-study-reproducing-bokehs-legend-example),
not a new mechanism. `legend_location` is proposed to ship together
with [8.2](#82-case-study-reproducing-bokehs-legend-example)'s
`legend_title` rather than separately, since both describe the same
`BaseSpec`-level "legend" concept and both are set together in this
example's own bokeh source.

### 8.4 Case study: reproducing bokeh's stacked bar example

Checked against
[bokeh's `stacked` bar chart example](https://docs.bokeh.org/en/latest/docs/examples/basic/bars/stacked.html)
(one `vbar_stack` call stacking three year-series on top of each other
per fruit, a categorical (string) x-axis, a fixed 3-color palette, a
horizontal legend pinned top-left, hover tooltips, and assorted
chrome removal -- no gridlines, no minor ticks, no plot outline) to
see whether it is reproducible through plotmux's unified API,
unchanged, on all five backends. Unlike
[8.1](#81-case-study-reproducing-bokehs-slope-example)/[8.2](#82-case-study-reproducing-bokehs-legend-example)/[8.3](#83-case-study-reproducing-bokehs-log-plot-example),
this is not close to reproducible: it needs one significant new
capability, hits a portability gap in an existing one, and legitimately
sits in [1](#1-goal)'s stated non-goal territory for the rest.

- **Stacking.** No plotmux equivalent at all: `BarSpec` (see
  [4.9](#49-specifying-colors-across-backends)) is a single series, and
  `layer()`'s `BarSpec` support (see
  [4.8](#48-layering-multiple-specs-on-one-axes)) draws each child's
  bars independently onto the shared axes with no coordination between
  them -- several `BarSpec`s at the same `x` positions simply overlap
  (each fully drawn, the last child on top), they do not stack into
  cumulative segments the way `vbar_stack` does. This is a real gap,
  not a documentation nuance: today's `layer()` mechanism has no path
  to bokeh's stacking behavior at all, unlike, say, marker shape or
  legend title, which are one new field away. Candidate fix: a new
  chart type, `StackedBarSpec(x, series: tuple[BarSeries, ...])` (a
  small per-series `(y, label, color)` tuple, mirroring how
  `LayerSpec.layers` holds a tuple of children) rather than overloading
  `layer()` -- stacking is fundamentally a different composition rule
  from layering (cumulative y-offset vs. shared axes), so it earns its
  own spec and its own `_RENDERERS` entry per backend, the same
  reasoning that gave `BarSpec` itself its own spec rather than folding
  it into `HistogramSpec` (see [3.2](#32-package-layout)):
  matplotlib `Axes.bar(..., bottom=running_total)`, incrementing
  `running_total` per series (matplotlib's own idiom for a stacked
  bar, no native stacking primitive); bokeh
  `figure.vbar_stack(names, x=..., source=...)` directly (bokeh's own
  primitive, matched almost one-to-one); altair
  `mark_bar().encode(x=..., y=..., color=...)` with the data reshaped
  long-form (one row per `(x, series)` pair) -- Vega-Lite stacks a bar
  mark automatically whenever `y` is quantitative and `color` is a
  discrete encoding, no explicit stacking argument needed; plotly
  `go.Bar` per series plus `fig.update_layout(barmode="stack")`; xy
  would need its own equivalent checked against its bar-chart API
  (unclear whether `xy.bar_chart` has a native stacking mode or would
  need the same running-total approach as matplotlib).
- **Categorical (string) x-axis.** `BarSpec.x` (see
  [4.9](#49-specifying-colors-across-backends)) is typed and
  documented as an array of positions, and every renderer reflects
  that assumption inconsistently across backends when `x` actually
  holds strings (e.g. `fruits = ["Apples", "Pears", ...]`, this
  example's own `x`):
  - matplotlib: works today, unchanged -- `Axes.bar` accepts a string
    `x` natively and draws categorical ticks.
  - plotly: works today, unchanged -- `go.Bar(x=...)` accepts a string
    `x` natively the same way.
  - bokeh: **broken**. `BokehBackend`'s shared `_make_renderer` (see
    `plotmux.backends.bokeh.backend`) always constructs
    `bokeh_figure(x_axis_type=spec.xscale, ...)` with bokeh's default
    linear numeric `x_range`; bokeh requires a categorical
    `FactorRange` x_range (typically `figure(x_range=fruits)`, as this
    example's own source sets explicitly) before a glyph is drawn with
    string x-values, or it raises. `plotmux.bar(fruits, counts,
    backend="bokeh")` fails outright today; matplotlib and plotly
    render the identical call correctly.
  - altair: **broken**. `render_bar` (see above) hardcodes
    `.encode(x="x:Q", y="y:Q")` -- the `:Q` (quantitative) type
    specifier -- rather than inferring or accepting a categorical
    (`:N`, nominal) type, so passing string `x` values produces
    invalid encoded data (altair/Vega-Lite expects numbers under a
    `:Q` field) rather than a categorical axis.
  - xy: unverified -- would need checking against `xy.bar`'s own
    x-axis type inference/argument.

  So a categorical x-axis is not a portable `BarSpec` feature today,
  only an accident of which backend happens to be selected -- the same
  shape of problem as [8.3](#83-case-study-reproducing-bokehs-log-plot-example)'s
  hollow-marker finding (works on one backend by that backend's own
  default, breaks or misbehaves on the others). Candidate fix: detect
  a non-numeric `spec.x` (e.g. `spec.x.dtype.kind in "US"`) in
  `BarSpec.__post_init__` or leave it to each renderer, and have
  bokeh's `_make_renderer` construct the `figure` with
  `x_range=list(spec.x)` when `x` is categorical (bokeh's `FactorRange`
  needs the ordered category list up front, so this bar-specific
  construction can no longer share the generic `_make_renderer` used
  by every other chart type unchanged -- it would need its own
  bokeh-specific wrapper, or `_make_renderer` itself would need an
  optional `figure_kwargs(spec)` hook), and altair's `render_bar` to
  encode `x="x:N"` instead of `x="x:Q"` in that case. This would need
  to land together with (or before) the stacking fix above, since
  `StackedBarSpec`'s own `x` has exactly the same categorical-vs-numeric
  question.
- **Legend orientation** (`p.legend.orientation = "horizontal"`). A
  third legend-chrome field, alongside
  [8.2](#82-case-study-reproducing-bokehs-legend-example)'s
  `legend_title` and [8.3](#83-case-study-reproducing-bokehs-log-plot-example)'s
  `legend_location`, that plotmux has no equivalent for. Natural to add
  as a third field in the same batch: `legend_orientation:
  Literal["vertical", "horizontal"] | None = None`, applied in
  `apply_common_style`: matplotlib `ax.legend(ncols=len(handles))` when
  `"horizontal"` (matplotlib has no direct orientation flag, only a
  column count, so horizontal is approximated as one row); bokeh
  `fig.legend.orientation = ...` directly (bokeh's own vocabulary,
  matched one-to-one); altair `alt.Legend(direction=...)`; plotly
  `fig.update_layout(legend=dict(orientation="h" if ... else "v"))`;
  xy would need its own equivalent checked against its legend API.

Deliberately **not** treated as gaps, matching [1](#1-goal)'s stated
non-goals:

- **Hover tooltips** (`tools="hover", tooltips="$name @fruits:
  @$name"`). An interactive, backend-specific power feature with no
  meaning on matplotlib (a static image) and no obvious common
  vocabulary across bokeh/plotly's very different tooltip-templating
  systems and altair's own `tooltip` encoding channel; reachable per
  backend via `Figure.to_native()` (see [4.3](#43-figure)), the
  documented escape hatch for exactly this kind of niche,
  backend-specific feature, not a candidate for the unified API.
- **Gridline/minor-tick/outline removal, `toolbar_location=None`,
  `x_range.range_padding`.** Fine-grained chrome cosmetics with no
  existing common-style precedent (unlike `background_color`, which
  *is* on `BaseSpec` because every backend has an equally central
  notion of "figure background"); same escape-hatch treatment as
  above.

None of the three real gaps above are scheduled (see
[8](#8-candidate-future-work)). Stacking is the first of this
document's four case studies to require a genuinely new spec type
rather than a new field on an existing one; the categorical-x-axis fix
is a prerequisite for stacking to be usable with string categories
(this example's own case) even though it is independently useful for
plain `BarSpec` today.
