# plotmux design

Status: implemented, current as of 2026-11-22. This document is the **current-state architecture
reference**: it describes `plotmux` as it exists today. For the chronological log of the case
studies and the redesign that produced it, see
[`docs/docs/dev/design_history.md`](docs/docs/dev/design_history.md). The plan the redesign
followed is [`review/target_state.md`](review/target_state.md).

The package in one sentence: **specs are plain data, the core turns them into three drawing
primitives, a backend only draws those primitives.**

## 1. Goal

`plotmux` is a lightweight abstraction layer over Python's plotting libraries: users write plotting
code once against the unified API and choose the rendering backend (`matplotlib`, `xy`, `bokeh`,
`altair`, `plotly`) at runtime. Swapping the backend is a one-line change, and adding a backend or
a chart type does not require changing existing code.

Scope: a small set of generic, broadly useful charts (histogram, empirical CDF, line, scatter, bar,
stacked bar, slope), layering them on one axes, laying panels out in a grid, common axes styling,
per-mark color, legend style and export. Non-goals: exposing every feature of every library, or
every possible plot type. Anything else is reachable through the escape hatch `Figure.to_native()`,
not by growing the unified API to the union of all backends. There is no keyword pass-through to
the library, so a call means the same on every backend.

Constraints that shape the design:

1. **Simple and easy to maintain.** The code that exists only because the design repeated the same
   work in every backend was removed instead of kept next to the new code.
2. **Same chart on every backend.** A design that is simpler but makes two backends draw different
   data for the same spec is rejected.
3. **The core stays small.** It imports only `coola` and `numpy`; every plotting library is
   optional, lazy and inside `plotmux.backends.<name>`.
4. **No new concept without a deletion.** A panel, a primitive and a scene each removed more code
   than they added (section 5).

## 2. Properties of the package

Each property names what enforces it, so a change that breaks a property breaks a test.

| Property                | Definition                                                                                                                                                                                                      | Enforced by                            |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Spec and render apart   | A spec is plain data: numbers, strings and colors, never a plotting-library object. Importing `plotmux.specs` imports no plotting library.                                                                      | `plotmux.specs`, `plotmux.scene`       |
| Same chart everywhere   | For one spec, every backend draws the same primitives (the same numbers). Only the idiom of the library (fonts, margins, grid lines) differs. Pixel identity is not promised.                                   | `plotmux.scene`, conformance test      |
| Complete support        | Every chart type works standalone, in a layer and in a grid, on every backend. The only per-backend differences are in `Backend.capabilities()` and are queryable.                                              | `plotmux.scene`, `BackendCapabilities` |
| Fail early, fail alike  | An invalid input raises `InvalidSpecError` when the spec is built, whatever the backend. A request a backend cannot honor raises `UnsupportedSpecError` or `UnsupportedFormatError` before any drawing or file. | specs, `Backend.render`, `export.save` |
| Typed errors            | Every exception is a `PlotmuxError` and also its builtin counterpart (`ValueError`, `RuntimeError`, `NotImplementedError`), with a message that names the value and the remedy.                                 | `plotmux.exceptions`                   |
| Immutable specs         | A spec cannot change after construction: fields are frozen, arrays are copied and read-only. Specs have value equality (and are not hashable). Rendering never modifies a spec.                                 | `plotmux.specs.base`                   |
| Deterministic           | The same spec on the same backend and library version gives the same native figure. No randomness, no hidden global style.                                                                                      | `plotmux.scene`                        |
| Lazy and optional       | `import plotmux` imports no plotting library, no backend module and no plugin. A backend is imported on first use. A missing library raises `BackendNotFoundError` with the extra.                              | `plotmux.backends.registry`            |
| Registry-extensible     | A new backend is one class found by name (built-in table, entry point, or `register_backend`). A new chart type is one spec with a `to_primitives` method and needs no backend change.                          | registry, `MarkSpec`                   |
| Small, with an escape   | The unified API covers generic charts only. Anything else goes through `Figure.to_native()`. A misspelled keyword is a `TypeError` of `plotmux`.                                                                | `plotmux.api`, `Figure`                |
| Context-safe default    | The default backend is a `ContextVar`: thread and task local. The only process-wide mutable state is the backend registry.                                                                                      | `plotmux.config`                       |
| Works where it is shown | `Figure.show()`, the notebook display and `Figure.save()` work on every backend, with the export formats the backend declares, validated before any file or directory is created.                               | `Backend.show`, `Backend.mimebundle`   |
| Typed and keyword-only  | Public options are keyword-only, fully typed (`ty` and `pyright` clean), documented with a runnable example.                                                                                                    | `CLAUDE.md`, CI                        |

Not guaranteed, and documented as such:

- **Pixel identity across backends**, interactivity, fonts, default margins and tooltips.
- **Static image export** for `bokeh`, `altair` and `plotly` without their optional exporters
  (Selenium, `vl-convert-python`, `kaleido`); `xy` grids export to HTML only.
- **Very large inputs.** An exact CDF of `n` values draws `2n` vertices; `nbins` bounds it. The
  native figures of `altair` and `plotly` embed the data.
- **Axes with non-positive data on a log scale**: the library decides what is drawn.
- **Limits with one bound** on `xy` and `plotly`: both libraries take the two bounds of a limit
  together, so a limit with a single bound is left to the autoscale.
- **Thread safety of registering a backend while another thread renders.** The registry is filled
  lazily; concurrent first use of the same backend can import it twice and keeps the first instance.

## 3. Architecture

```text
plotmux.hist(values, bins=30, title="t")             plotmux/api.py            builds specs, no logic
        |
        v
PanelSpec(marks=(HistogramSpec(...),), title="t")    plotmux/specs/            pure data, validated
        |   one panel = one axes; GridSpec = several panels
        v
build_scene(spec) -> AxesScene | GridScene            plotmux/scene.py          numpy only
        |   ranges, statistics, default colors, legend, categories,
        |   lowering of every mark to Bars | Line | Points
        v
Backend.draw(scene) -> native figure                  plotmux/backends/<name>/  3 draw functions,
        |   draws primitives, applies the axes style       1 style function, grid, save
        v
Figure(spec, backend_name, native)                    plotmux/figure.py         show / save / to_native
```

The core owns every decision that changes the numbers on the screen (ranges, bins, steps, stacking,
default colors, extents). A backend owns only the translation of three primitives and the axes
style into one library. A backend cannot forget a protection and cannot draw a different histogram.

### 3.1 Specs: marks, panels, grids

```python
@dataclass(frozen=True, eq=False)
class MarkSpec(Spec):  # what is drawn: data + mark style
    label: str | None; color: Color; alpha: float | None   # validated once, here
    def x_extent(self) -> tuple[float, float] | None: ...  # None: no data of its own
    def to_primitives(self, extent) -> tuple[Primitive, ...]: ...

@dataclass(frozen=True, eq=False)
class PanelSpec(Spec):  # one axes: marks + axes style
    marks: tuple[MarkSpec, ...]
    title, xlabel, ylabel, xscale, yscale, xmin, xmax, ymin, ymax, background_color
    legend_title, legend_location, legend_orientation

@dataclass(frozen=True, eq=False)
class GridSpec(Spec):  # independent panels
    panels: tuple[PanelSpec, ...]; ncols: int = 1; title: str | None = None
```

- **Marks** are `HistogramSpec`, `CdfSpec`, `BarSpec`, `StackedBarSpec`, `LineSpec`, `ScatterSpec`
  and `SlopeSpec`. `BarSeries` is one series of a stacked bar. The axes fields exist once, on
  `PanelSpec`.
- **A layer is a panel with several marks.** A panel holds marks and a grid holds panels, so the
  type forbids "a layer in a layer" and "a grid in a grid", and a grid of layers needs no special
  case. A mark with a `requires_extent` (a slope) is checked when the panel is built.
- **Range of a histogram or a CDF.** `xmin`/`xmax` of `HistogramSpec` and `CdfSpec` are the range of
  the data they bin or plot (a number, a quantile string such as `"q0.1"`, or `None`), resolved by
  `plotmux.utils.range.find_range`. They are not axis limits: the axes autoscale on the drawn
  primitives. An axis limit is `PanelSpec.xmin`/`xmax`, a number.
- **Immutability.** `Spec.__post_init__` helpers copy every array and make it read-only; `Spec`
  (through `plotmux.utils.equality.ValueObject`) gives value equality with `coola` and no hash.
- **Validation lives in the specs** and raises `InvalidSpecError`: lengths, dimensions, finite
  values, positive widths and sizes, color parsing, the order of limits, a slope with no extent,
  a categorical `x` mixed with a numeric `x` in one panel.
- **The input policy** of `NaN` and `inf` is in the specs: a histogram and a CDF drop them (a
  `UserWarning` gives the count, once per spec) and raise if no finite value is left; a line and a
  scatter keep `NaN` (a gap, no point) and reject `inf`. See `docs/docs/uguide/api.md`.
- **The extension point for a new chart type** is a `MarkSpec` subclass with `to_primitives`. If
  the chart is a composition of `Bars`, `Line` and `Points` (a box plot is: bars and lines), no
  backend changes.

### 3.2 Primitives and the scene

`plotmux.primitives` defines the three drawing primitives, frozen dataclasses with value equality:

| Primitive | Used by                                      | Fields                                                                                                         |
| --------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `Bars`    | histogram, bar, stacked bar (one per series) | `x` (centers or categories), `height`, `base`, `width`, `color`, `alpha`, `label`                              |
| `Line`    | line, CDF steps, slope                       | `x`, `y`, `infinite` (`(gradient, intercept)` of a slope), `color`, `alpha`, `linewidth`, `linestyle`, `label` |
| `Points`  | scatter                                      | `x`, `y`, `color`, `alpha`, `size`, `marker`, `fill`, `edgecolor`, `label`                                     |

`plotmux.scene.build_scene(spec)` is a pure function of the spec:

1. resolve the x extent of the panel: `PanelSpec.xmin`/`xmax` where set, else the union of the
   `x_extent()` of the marks that have data;
2. call `to_primitives(extent)` on each mark, in order;
3. give a color of `DEFAULT_PALETTE` (cycling, in drawing order) to each primitive whose color is
   `None`. **Every** uncolored primitive gets one, the first of a single-mark chart included, so the
   swap of the backend does not change the color. An explicit color does not consume a slot;
4. the legend exists if and only if one primitive has a label;
5. collect the categories of the panel in order of first appearance.

An `AxesScene` holds the primitives, the title, the labels, the scales, the limits, the background
color (an RGBA tuple), the `LegendStyle` and the categories; a `GridScene` holds the `AxesScene` of
each panel, `ncols` and the title.

| Mark             | Primitives                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `HistogramSpec`  | `Bars`: `np.histogram(values, bins, range=find_range(...), density)`; `x` = bin centers, `width` = bin widths |
| `BarSpec`        | `Bars`: `x`, `height=y`, `base` = 0, `width`                                                                  |
| `StackedBarSpec` | one `Bars` per series, `base` = running total of the previous series                                          |
| `CdfSpec`        | `Line`: the step vertices of the exact empirical CDF; `nbins` bins the values first                           |
| `LineSpec`       | `Line`                                                                                                        |
| `ScatterSpec`    | `Points`                                                                                                      |
| `SlopeSpec`      | `Line` with two endpoints `(lo, g * lo + b)` and `(hi, g * hi + b)`, over the panel x extent                  |

The CDF is the empirical `P(X <= x)` over **all** the values: `xmin`/`xmax` restrict the vertices
that are drawn and do not renormalize the curve.

### 3.3 The slope: a segment everywhere, a native line where it exists

The x extent of a panel is its explicit `xmin`/`xmax` where given, else the extent of its data-bound
marks. A `SlopeSpec` with no extent raises `InvalidSpecError` when the panel is built. The lowering
of a slope is a `Line` with the two endpoints of the extent, so every backend can draw it with
`draw_line` and no new primitive exists. The `Line` also carries `infinite=(gradient, intercept)`,
an **optional optimization of `draw_line`**: `matplotlib` (`Axes.axline`) and `bokeh`
(`models.Slope`) draw the native infinite line, which keeps extending when the user zooms past the
extent; the other backends ignore the field and draw the segment. The extent still comes from the
scene, so the autoscale and the conformance test see the same endpoints on every backend. A labeled
slope on `bokeh` is drawn as the segment, because a `Slope` has no legend entry.

### 3.4 The backend contract

```python
class Backend(ABC):
    name: ClassVar[str]

    @abstractmethod
    def capabilities(self) -> BackendCapabilities: ...  # formats, legend locations, markers
    @abstractmethod
    def draw(self, scene: AxesScene | GridScene) -> Any: ...  # the native figure
    @abstractmethod
    def save(self, native, path, fmt) -> None: ...
    def show(self, native) -> None: ...  # default: NotImplementedError
    def mimebundle(self, native) -> dict | None: ...  # default: the repr of the native object

    def render(self, spec: FigureSpec) -> Any:  # concrete, not overridden
        scene = build_scene(spec)
        self.capabilities().check(scene)  # UnsupportedSpecError, before drawing
        return self.draw(scene)
```

- A backend implements `draw`, `save`, `capabilities` and, where the library needs it, `show` and
  `mimebundle`. Each backend has two modules: `backend.py` (`draw_bars`, `draw_line`, `draw_points`,
  the composition of a grid, `save`) and `style.py` (`apply_style` and the translation tables).
  `xy` also keeps `grid.py` for the layout of its grid.
- **Capabilities are data**, checked by the base class before drawing:
  `BackendCapabilities(name, formats, grid_formats, legend_locations, markers)`. `check(scene)` raises
  `UnsupportedSpecError` (naming the backend and the supported values) for a legend location or a
  marker outside the sets; `check_format(fmt, grid=...)` raises `UnsupportedFormatError`. There is
  no `"best"` legend location: three backends have no automatic placement. `Figure.supported_formats`
  reads the capabilities.
- **Display is owned by the backend.** `Figure.show()` calls `backend.show(native)` and the notebook
  display calls `backend.mimebundle(native)`; a figure forwards no other attribute to the native
  object.
- **No keyword pass-through.** `render(spec)` takes nothing else. The escape hatch is the native
  figure, which the user modifies after the render.

How each library draws the primitives:

| Backend      | Bars                                   | Line                                  | Points                         | Grid                              |
| ------------ | -------------------------------------- | ------------------------------------- | ------------------------------ | --------------------------------- |
| `matplotlib` | `Axes.bar` (`bottom`, array `width`)   | `Axes.plot`; a slope is `Axes.axline` | `Axes.scatter`                 | `Figure.subplots`                 |
| `xy`         | `xy.bar` (`base`, array `width`)       | `xy.line`                             | `xy.scatter`                   | `XyGrid` (iframes, HTML only)     |
| `bokeh`      | `vbar` (`bottom`, `top`, array width)  | `figure.line`; a slope is `Slope`     | `figure.scatter`               | `gridplot`, a `Div` for the title |
| `plotly`     | `go.Bar` (`base`), `barmode="overlay"` | `go.Scatter` in `lines` mode          | `go.Scatter` in `markers` mode | `make_subplots`                   |
| `altair`     | `mark_bar` with `x`/`x2`, `y`/`y2`     | `mark_line`                           | `mark_point`                   | `alt.concat`                      |

`altair` writes the data of a primitive as one CSV string with an explicit `parse` of each column:
Vega-Lite schema validation of a list of records is row by row (3.4 s for 100,000 points), while a
string is validated in constant time.

### 3.5 The registry

`plotmux.backends.registry` finds a backend by name, in this order: an instance registered with
`register_backend(backend, *, replace=False)`, the built-in table of `"module:Class"` strings, then
the entry-point group `plotmux.backends`. `get_backend(name)` imports **only the module of that
name** on the first request, instantiates the class once and caches it. An `ImportError` becomes
`BackendNotFoundError` with the extra to install and the original error as the cause.

- The entry point value is `package.module:BackendClass`, with no import-time side effect.
  `import plotmux` reads no entry point; `known_backend_names()` reads their names from the installed
  metadata, which imports nothing, and `set_backend` rejects an unknown name at the call site.
- A built-in name cannot be taken over by a plugin: it calls `register_backend(..., replace=True)`
  explicitly. The order of precedence is an explicit `replace=True`, then a built-in backend, then an
  entry point.
- `available_backends()` lists the usable names, using the `is_*_available()` helpers of
  `plotmux.utils.imports`.

A third-party backend ships as an independent package: one class with `capabilities`, `draw` and
`save`, and one entry point.

### 3.6 `Figure`, `export`, `config`

- `Figure(spec, backend_name, native)` is a slotted dataclass with `show()`, `save(path)`,
  `to_native()`, `supported_formats` and the two display hooks. `spec` is a `PanelSpec` or a
  `GridSpec`.
- `export.save(figure, path)` sanitizes the path, takes the format from the suffix, validates it
  against `capabilities().formats` (or `grid_formats` for a grid) **before** creating the directory,
  then calls `backend.save`.
- `config` holds the default backend in a `ContextVar` (`set_backend`, `backend()`), which makes it
  thread and task local.

### 3.7 The public API

`api.py` builds specs and calls one `_render`. The axes options are declared once as a `TypedDict`
and documented once:

```python
class PanelOptions(TypedDict, total=False):
    title; xlabel; ylabel; xscale; yscale; ymin; ymax; background_color
    legend_title; legend_location; legend_orientation; backend

class BoundedPanelOptions(PanelOptions, total=False):  # adds the axis limits
    xmin: float | None; xmax: float | None

def hist(values, *, bins=30, xmin=None, xmax=None, density=False, label=None, color=None,
         alpha=None, **panel: Unpack[PanelOptions]) -> Figure: ...
```

`hist` and `cdf` take `PanelOptions` (their `xmin`/`xmax` are the data range); the other charts and
`layer` take `BoundedPanelOptions`. A misspelled keyword is a `TypeError` of the function the user
called, with the valid names.

- `layer(*items, **panel)` accepts marks and single-panel `Figure` objects. A `Figure` contributes
  its marks. The axes options of the call are used; where the call leaves one unset, the unique
  non-default value of the figures is used; two different non-default values raise
  `InvalidSpecError`.
- `grid(*items, ncols=1, title=None, backend=None)` accepts panels, marks (wrapped in a default
  panel) and single-panel `Figure` objects. It exposes no axis option: each panel keeps its own.
- The nine functions are `hist`, `bar`, `stacked_bar`, `cdf`, `line`, `scatter`, `slope`, `layer`
  and `grid`.

### 3.8 Colors

`plotmux.colors.parse_color` turns a hex string, a CSS/matplotlib named color or an RGB(A) tuple
into one canonical RGBA tuple of floats in `[0, 1]`, using a bundled table of named colors (no
matplotlib import). Specs hold the parsed color; the scene gives the default palette color; each
backend converts the RGBA tuple to its native representation (`rgba_to_xy`, `rgba_to_bokeh`,
`rgba_to_plotly`, `rgba_to_altair`, or the tuple itself for `matplotlib`).
`PRIMARY`, `SECONDARY`, `TERTIARY` and `DEFAULT_PALETTE` are the predefined colors.

## 4. Support

Every chart type works standalone, in a layer and in a grid, on every backend: the conformance test
(`tests/integration/conformance/`) draws each mark in the three contexts on the five backends (150
cases) and checks that what the native figure draws equals the primitives of `build_scene`. The
remaining differences are declared in `Backend.capabilities()` and are queryable:

| Backend      | Export formats of a figure                         | Export formats of a grid | Legend locations | Markers |
| ------------ | -------------------------------------------------- | ------------------------ | ---------------- | ------- |
| `matplotlib` | `png`, `svg`, `pdf`, `jpg`, `jpeg`                 | the same                 | the 8 portable   | all 6   |
| `xy`         | `png`, `jpg`, `jpeg`, `webp`, `svg`, `pdf`, `html` | `html`                   | the 8 portable   | all 6   |
| `bokeh`      | `html`                                             | `html`                   | the 8 portable   | all 6   |
| `altair`     | `html`, `json`                                     | the same                 | the 8 portable   | all 6   |
| `plotly`     | `html`, `json`                                     | the same                 | the 8 portable   | all 6   |

The 8 portable legend locations are `top_left`, `top_right`, `bottom_left`, `bottom_right`, `top`,
`bottom`, `left` and `right`; the 6 markers are `circle`, `square`, `triangle`, `diamond`, `cross`
and `x`. A request outside the declared sets raises before drawing. The idiom differences that are
not errors: `plotly` has one legend and one title per figure (a grid takes the legend of its first
panel that has one), `altair` shows the background as the `view` background, `xy` and `plotly` take
the two bounds of a limit together.

## 5. Size

Measured on `main` before the redesign and after it (code lines exclude docstrings, comments and
blank lines):

| Part                        | Before: code / with docstrings | After: code / with docstrings |
| --------------------------- | ------------------------------ | ----------------------------- |
| package (`src/plotmux`)     | 3,859 / 9,683 (95 modules)     | 2,837 / 7,178 (54 modules)    |
| the five `backends/<name>`  | 2,187 / 5,269 (60 modules)     | 982 / 2,429 (16 modules)      |
| `scene.py`, `primitives.py` | 0                              | 134 / 404                     |
| `utils/slope.py`            | 32 / 76                        | removed                       |

Render time after the redesign (warm, in milliseconds; 1,000,000 values for `hist` and `cdf` with
`nbins=100`, 100,000 points for `line`), against the numbers measured on `main` before it (`hist` 8
to 17 and `cdf` 7 to 17 on all five backends, `line` 0 to 5 on four backends and 3,421 on `altair`):

| Backend      | `hist` | `cdf` | `line` |
| ------------ | ------ | ----- | ------ |
| `matplotlib` | 16     | 10    | 4      |
| `xy`         | 7      | 7     | 0.2    |
| `bokeh`      | 13     | 12    | 5      |
| `altair`     | 8      | 8     | 100    |
| `plotly`     | 10     | 9     | 2      |

`build_scene` takes 10 ms for a histogram of 1,000,000 values and 4 ms for an exact CDF of 100,000
values. `tests/integration/test_performance.py` guards the scene and the `altair` line with bounds
about 20 times these times.

## 6. Why this shape

- **Works for any backend, not just today's five.** Nothing outside a `backends/<name>/` subpackage
  special-cases a backend by name: `Figure`, `export`, `config` and `api` only go through `Backend`
  and the registry. This is the bar any future backend must also clear, including one added as a
  third-party plugin.
- **The engine owns the invariants.** It is the same split as `coola.recursive` (the engine owns the
  invariants, a transformer describes the shape of a type), applied to rendering. A backend that
  draws three primitives cannot forget a protection and cannot draw a different histogram.
- **Extensibility.** A new backend is one class with `capabilities`, `draw` and `save`. A new chart
  type is one `MarkSpec` with `to_primitives`, and needs no backend change when it is a composition
  of bars, lines and points.
- **Optional dependencies stay optional, and cheap.** `utils`, `specs`, `scene`, `colors`, `figure`,
  `config`, `api` and `export` are always importable; a backend subpackage is imported when its name
  is requested, so a process using one backend never imports the other four.
- **Testability.** Specs, lowering and the scene are plain numpy and unit-tested with literal
  arrays. The backends get a thin test layer and the conformance test.
- **No leaky abstraction trap.** `Figure.to_native()` means that "unified API" does not have to mean
  "least common denominator forever".

## 7. Candidate future backends

`matplotlib` (static), `xy` (interactive HTML), `bokeh` (interactive), `altair` (declarative
Vega-Lite) and `plotly` (interactive, native Jupyter and Dash support) are implemented. Remaining
candidate: **plotnine** (ggplot2-style), which matches users coming from R and is mostly static like
`matplotlib`. Not scheduled: a backend is two modules (`backend.py`, `style.py`) and one
`pyproject.toml` extra, or an entirely external package using the entry-point mechanism. Picking one
should be driven by user requests.

## 8. Open questions

- **Chart types.** Histogram, CDF, line, scatter, bar, stacked bar and slope were picked as "generic
  and broadly useful", but that bar is not written down. A box plot is a composition of `Bars` and
  `Line`: is that composition generic enough, or does the project need an explicit checklist before
  adding an eighth mark?
- **Default style beyond color.** The default palette is assigned by `build_scene`. Should other
  default style (fonts, sizes) follow, or live on `config` so that a user sets one theme for a whole
  session the way `set_backend` sets one backend?
- **Figure size, DPI, theme and fonts.** No unified option exists (there is no keyword pass-through
  either); `to_native()` is the way. A `size=(width, height)` option is the natural next addition
  and is a separate design.
- **Partial limits on `xy` and `plotly`.** Both libraries take the two bounds of an axis limit
  together. Filling the missing bound from the extent of the data would make the limit portable.
- **Stacked bars with negative values.** The running total is a plain cumulative sum, as it always
  was.

## 9. Candidate future work

None of the following is scheduled.

- A sixth backend, most likely `plotnine`, evaluated per section 7.
- An eighth mark such as a box plot, once one clears the bar of section 8.
- Secondary axes, annotations, subplots sharing axes and dates on an axis: out of scope, as before.
