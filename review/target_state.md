# `plotmux`: target state and the changes to reach it

This document describes the design `plotmux` should have, then the changes to make to the current
implementation (`main`, `be6174a`) to get there. It follows the principles of the documentation
(`DESIGN.md` sections 1, 3 and 5; `docs/docs/dev/architecture.md`; the user guides in
`docs/docs/uguide/`): separate the spec from the render, one-line backend swap, optional and lazy
dependencies, extension by registration, a small generic scope with an escape hatch. Its aim is a
small package that is easy to maintain: **specs are plain data, the core turns them into three
drawing primitives, a backend only draws those primitives**. Breaking changes are accepted, and the
future state is more important than the past one.

Evidence comes from probes run on `main` (Python 3.14, the five backends installed, scripts kept
outside the repository) and from reading the code. Items marked **[verified]** were reproduced;
**[reading]** comes from the code or the documentation. No prototype of the new design was written,
so every claim about the target is a design claim, and section 8 lists the gates that must prove
them. Nothing in `src`, `tests` or `docs` was changed.

## Constraints

1. **Simple and easy to maintain.** The package is 9,651 lines of Python, 5,706 of them in
   `backends/` (about 1,520 once docstrings are removed) spread over 63 modules: 12 modules per
   backend, one per chart type per backend. The target removes the code that exists only because the
   design repeats the same work in every backend, instead of adding code next to it.
2. **Major release.** Breaking changes are fine and compatibility is not a design input: no alias,
   no deprecation period, no shim for the old spec classes. The release notes list the changes.
3. **Same chart on every backend.** "Swapping the backend is a one-line change" is the promise of
   the package. A design that is simpler but makes two backends draw different data for the same
   spec is rejected.
4. **The core stays small.** The core imports only `coola` and `numpy` (`CLAUDE.md`); every plotting
   library stays lazy and inside `plotmux.backends.<name>`.
5. **No new concept without a deletion.** Each new concept of section 3 (a panel, a primitive, a
   scene) must remove more code than it adds; the size table of the appendix is the check.

## 1. Properties of the package

These are the properties the package guarantees. Each one names what enforces it, so a change that
breaks a property breaks a test (section 8).

| Property                | Definition                                                                                                                                                                                                        | Enforced by                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Spec and render apart   | A spec is plain data: it holds numbers, strings and colors, never a plotting-library object, and importing `plotmux.specs` imports no plotting library. A backend turns it into a native figure.                  | `plotmux.specs`, `plotmux.scene`             |
| Same chart everywhere   | For one spec, every backend draws the same primitives (the same numbers). Only the idiom of the library (fonts, margins, grid lines) differs. Pixel identity is not promised.                                     | `plotmux.scene` (lowering), conformance test |
| Complete support        | Every chart type works standalone, in a layer and in a grid, on every backend. The only per-backend differences are listed in `Backend.capabilities()` (export formats, legend locations, markers) and queryable. | `plotmux.scene`, `BackendCapabilities`       |
| Fail early, fail alike  | An invalid input raises `InvalidSpecError` when the spec is built, whatever the backend. A request a backend cannot honor raises `UnsupportedSpecError` or `UnsupportedFormatError` before any drawing.           | specs, `Backend.render`, `export.save`       |
| Typed errors            | Every exception is a `PlotmuxError` and also its builtin counterpart (`ValueError`, `RuntimeError`, `NotImplementedError`), with a message that names the value and the remedy.                                   | `plotmux.exceptions`                         |
| Immutable specs         | A spec cannot change after construction: fields are frozen and arrays are copied and read-only. Specs have value equality. Rendering never modifies a spec or the caller's arrays.                                | `plotmux.specs.base`                         |
| Deterministic           | The same spec on the same backend and library version gives the same native figure. No randomness, no hidden global style.                                                                                        | `plotmux.scene`                              |
| Lazy and optional       | `import plotmux` imports no plotting library, no backend module and no plugin. A backend is imported on first use. A missing library raises `BackendNotFoundError` with the extra to install.                     | `plotmux.backends.registry`                  |
| Registry-extensible     | A new backend is one class found by name (built-in table, entry point, or `register_backend`). A new chart type is one spec with a `to_primitives` method and needs no backend change.                            | registry, `MarkSpec`                         |
| Small, with an escape   | The unified API covers generic charts only. Anything else goes through `Figure.to_native()`. There is no keyword pass-through to the library, so a call means the same on every backend.                          | `plotmux.api`, `Figure`                      |
| Context-safe default    | The default backend is a `ContextVar`: thread and task local. The only process-wide mutable state is the backend registry.                                                                                        | `plotmux.config`                             |
| Works where it is shown | `Figure.show()`, the notebook display and `Figure.save()` work on every backend, with the export formats the backend declares, validated before any file or directory is created.                                 | `Backend.show`, `Backend.mimebundle`         |
| Typed and keyword-only  | Public options are keyword-only, fully typed (`ty` and `pyright` clean), documented with a runnable example.                                                                                                      | `CLAUDE.md`, CI                              |

Not guaranteed, and documented as such:

- **Pixel identity across backends**, interactivity, fonts, default margins and tooltips.
- **Static image export** for `bokeh`, `altair` and `plotly` without their optional exporters
  (Selenium, `vl-convert-python`, `kaleido`); `xy` grids export to HTML only.
- **Very large inputs.** An exact CDF of `n` values draws `2n + 1` vertices; the user passes `nbins`
  to bound it (decision D4). Native figures of `altair` and `plotly` embed the data.
- **Axes with non-positive data on a log scale**: the library decides what is drawn.
- **Thread safety of registering a backend while another thread renders.** The registry is filled
  lazily; concurrent first use of the same backend can import it twice and keeps the first
  instance.

## 2. What differs today

| #   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Status         |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| F1  | **A spec mixes the mark and the axes.** Every chart spec carries `title`, `xlabel`, `ylabel`, `xscale`, `yscale`, `ymin`, `ymax`, `background_color` and three legend fields (`BaseSpec`). In a `LayerSpec` the fields of the children are accepted and silently ignored (`LineSpec(title="child", yscale="log")` is kept and not applied). `GridSpec` inherits four fields every backend ignores. `XBoundSpec` and the redeclared `xmin`/`xmax` of `HistogramSpec`/`CdfSpec` exist to work around this.                                                                | **[verified]** |
| F2  | **The support matrix is irregular.** `SlopeSpec` works standalone on `matplotlib` and `bokeh` only, in a layer on all five, and in a grid on none (even where it works standalone). `StackedBarSpec` works standalone on all five and in a layer or a grid on none. See the appendix table.                                                                                                                                                                                                                                                                             | **[verified]** |
| F3  | **The same spec draws different things.** `CdfSpec(nbins=None)` uses the library default on `matplotlib` (`Axes.hist` takes `rcParams["hist.bins"]`, which is 10) and 100 bins on `xy` and `bokeh`. The "empirical CDF" is a binned approximation. With an explicit `xmin`/`xmax` the counts and the normalisation are computed inside the range only, so the curve goes from 0 to 1 over the range instead of showing `P(X <= x)`. `BarSpec.width` is ignored on `altair`; `ScatterSpec(marker="x")` falls back on `altair`.                                           | **[reading]**  |
| F4  | **The same statistic is computed by up to five code paths.** `find_range` is called in 10 backend modules (5 histograms, 5 CDFs); the histogram counts come from `np.histogram` in three backends, from `Axes.hist` in `matplotlib` and from `xy.hist` in `xy`; the cumulative steps from `compute_cdf_steps` in four backends and `Axes.hist` in the fifth; a stacked bar is stacked by `matplotlib` itself (running total), by `xy` (`mode="stacked"`), `bokeh` (`vbar_stack`), `altair` (native stacking) and `plotly`, so the stacking rule is five different ones. | **[reading]**  |
| F5  | **Specs are frozen but not immutable, comparable or hashable.** `LineSpec(x=a, y=a)` keeps a reference to the caller's array (`a[0] = 99` changes `spec.x[0]`). `LineSpec(...) == LineSpec(...)` raises `ValueError: The truth value of an array ...`; `hash(spec)` raises `TypeError`.                                                                                                                                                                                                                                                                                 | **[verified]** |
| F6  | **`Figure.show()` fails on two of five backends, including the default.** `matplotlib`: `AttributeError: Figure.show works only for figures managed by pyplot`; `bokeh`: `NotImplementedError ... does not support 'show'`. The notebook display relies on a monkeypatched `_repr_png_` (`setattr(fig, "_repr_png_", ...)  # noqa: B010`) and a `Figure.__getattr__` that forwards a closed set of dunder names.                                                                                                                                                        | **[verified]** |
| F7  | **`**kwargs` pass-through undermines the swap.** Each plotting function forwards `**kwargs` to the library call of each mark (and to every child of a layer). A typo (`colour="red"`) raises an error from inside the library with five different types (`AttributeError`, `TypeError`, `SchemaValidationError`, `ValueError`) and no mention of `plotmux`; a valid library option makes the call backend specific. It cannot set a figure-level option (size), it is passed to the mark.                                                                               | **[verified]** |
| F8  | **Plugins are imported at `import plotmux`.** `plotmux/__init__.py` calls `load_entry_point_backends()`, which imports every third-party module of the `plotmux.backends` group. A plugin is a module with an import-time `register_backend(...)` side effect; whichever registers last for a name wins, including over a built-in.                                                                                                                                                                                                                                     | **[reading]**  |
| F9  | **Capabilities are prose.** `BackendCapabilities` holds `spec_types` (the keys of `_RENDERERS`) and `caveats`, free-text strings. A caller cannot ask "can this backend draw a slope in a grid?" or "which legend locations?"; layer and grid support is not represented at all.                                                                                                                                                                                                                                                                                        | **[reading]**  |
| F10 | **The input policy is undefined.** `hist`/`cdf` accept `NaN` silently (`find_range` is nan-aware, `np.histogram` drops values outside the explicit range, and raises without a range); `line` accepts `inf` on every backend; a categorical `x` mixed with numeric marks in one layer is not checked. Nothing documents or tests these cases.                                                                                                                                                                                                                           | **[verified]** |
| F11 | **Boilerplate.** `api.py` is 849 lines of repeated parameter lists and docstrings. The check `alpha must be in the range [0, 1]` is written 7 times. The block that resolves the slope range and raises the same `UnsupportedSpecError` is copied in the `xy`, `plotly` and `altair` layer modules. Each backend repeats a `_make_renderer` wrapper and a dispatch table for layers.                                                                                                                                                                                    | **[reading]**  |
| F12 | **`altair` is slow on line data.** A `line` of 100,000 points takes 3.4 s on `altair` against 2 to 5 ms on the four others; histograms and CDFs are 8 to 17 ms on all five (1,000,000 values). The cause was not diagnosed (the list-of-dicts data and the schema validation are suspects).                                                                                                                                                                                                                                                                             | **[verified]** |
| F13 | **The documentation contradicts the code.** `DESIGN.md` (1,558 lines, which duplicates `docs/docs/dev/architecture.md`) lists four extras and "the four built-in backend subpackages" (there are five), and its first open question asks whether `colors/` may depend on matplotlib: `colors/parser.py` uses a bundled table and imports no matplotlib. Section 9 and 7 mix finished work and open work.                                                                                                                                                                | **[reading]**  |

What is already right and must not regress: the spec and render split; lazy backend imports; the
`ContextVar` default backend; the exception hierarchy; `known_backend_names()` validating a backend
name without importing; the bundled named-color table (`parse_color` needs no matplotlib); export
validation before the directory is created; the `Figure.to_native()` escape hatch; the same
histogram bins on four backends (`np.histogram` with the same range); the keyword-only options.

## 3. Architecture

```text
plotmux.hist(values, bins=30, title="t")             plotmux/api.py            (about 350 lines)
        |   builds specs, no logic
        v
PanelSpec(marks=(HistogramSpec(...),), title="t")    plotmux/specs/            pure data, validated
        |   one panel = one axes; GridSpec = several panels
        v
build_scene(spec) -> AxesScene | GridScene            plotmux/scene.py          numpy only
        |   defaults (palette), ranges, statistics, categorical check,
        |   lowering of every mark to Bars | Line | Points
        v
Backend.draw(scene) -> native figure                  plotmux/backends/<name>/  3 draw functions,
        |   draws primitives, applies the axes style       1 style function, grid, save
        v
Figure(spec, backend_name, native)                    plotmux/figure.py         show / save / to_native
```

The core owns every decision that changes the numbers on the screen (ranges, bins, steps, stacking,
default colors, extents). A backend owns only the translation of three primitives and the axes
style into one library. That is the same split as `coola.recursive` (the engine owns the
invariants, a transformer describes the shape of a type), applied to rendering: a backend cannot
forget a protection and cannot draw a different histogram.

### 3.1 Specs: marks, panels, grids

```python
@dataclass(frozen=True, eq=False)
class Spec:                                  # value equality through coola, written once
    def __eq__(self, other): ...            # type(self) is type(other) and objects_are_equal
    __hash__ = None


@dataclass(frozen=True, eq=False)
class MarkSpec(Spec):                        # what is drawn: data + mark style
    label: str | None = None
    color: Color = None
    alpha: float | None = None               # validated once, here
    def x_extent(self) -> tuple[float, float] | None: ...        # None: no data of its own
    def to_primitives(self, extent) -> tuple[Primitive, ...]: ...


@dataclass(frozen=True, eq=False)
class PanelSpec(Spec):                       # one axes: marks + axes style
    marks: tuple[MarkSpec, ...]
    title, xlabel, ylabel: str | None
    xscale, yscale: Literal["linear", "log"]
    xmin, xmax, ymin, ymax: float | None
    background_color: Color
    legend_title: str | None
    legend_location: Literal["top_left", ..., "right"] | None      # no "best"
    legend_orientation: Literal["vertical", "horizontal"] | None


@dataclass(frozen=True, eq=False)
class GridSpec(Spec):                        # independent panels
    panels: tuple[PanelSpec, ...]
    ncols: int = 1
    title: str | None = None
```

- **Marks** are `HistogramSpec`, `CdfSpec`, `BarSpec`, `StackedBarSpec`, `LineSpec`, `ScatterSpec`
  and `SlopeSpec`, with the names and fields they have today minus the figure-level ones. `label`,
  `color` and `alpha` live on `MarkSpec` and are validated once (F11). `BarSeries` is kept.
- **A layer is a panel with several marks.** `LayerSpec` disappears: there is nothing left for it to
  do. "Layers may not nest" and "a grid cell may not be a grid" stop being runtime checks: a panel
  holds marks (a tuple of `MarkSpec`) and a grid holds panels, so the type forbids both. A grid of
  layers needs no special case.
- **Axes fields exist once**, on `PanelSpec` (F1). `XBoundSpec`, the shadowing of `xmin`/`xmax` and
  the ignored fields of `GridSpec` are deleted. `ymin <= ymax` and `xmin <= xmax` are checked in
  `PanelSpec.__post_init__`.
- **Range of a histogram or a CDF.** `HistogramSpec` and `CdfSpec` keep `xmin`/`xmax` as the range
  of the data they bin or plot (a number, a quantile string such as `"q0.1"`, or `None`), resolved
  by `find_range`. They no longer force the axis limits: the axes autoscale on the drawn
  primitives. An axis limit is `PanelSpec.xmin`/`xmax`, a number.
- **Immutability** (F5). `Spec.__post_init__` helpers copy every array with `np.array(...)` and
  set `flags.writeable = False`; `__eq__` is `coola.objects_are_equal` on the fields, written once.
  The spec is not hashable (it holds arrays); `Figure` hashes by identity.
- **Validation lives in the specs** and raises `InvalidSpecError`: lengths, dimensions, finite
  values for histograms and CDFs with a warning when some are dropped (decision D5), positive widths and sizes, color parsing, a
  `SlopeSpec` with no x extent (3.3), categorical `x` mixed with numeric marks in one panel.
- **The extension point for a new chart type** is a `MarkSpec` subclass with `to_primitives`. If the
  chart is a composition of `Bars`, `Line` and `Points` (a box plot is: bars and lines), no backend
  changes. This replaces "one renderer in every backend and one entry in every table".

### 3.2 Primitives and the scene

```python
@dataclass(frozen=True)
class Bars:  # histogram, bar, stacked bar (one Bars per series)
    x: np.ndarray  # centers (float) or categories (str)
    height: np.ndarray
    base: np.ndarray  # zeros, or the running total of a stacked bar
    width: float | np.ndarray  # data units; a fraction of the band when x is categorical
    color: RGBA
    alpha: float | None
    label: str | None


@dataclass(frozen=True)
class Line:  # line, CDF steps, slope (two endpoints)
    x: np.ndarray
    y: np.ndarray
    infinite: tuple[float, float] | None  # (gradient, intercept) of a slope, else None
    color: RGBA
    alpha: float | None
    linewidth: float | None
    linestyle: str
    label: str | None


@dataclass(frozen=True)
class Points:  # scatter
    x: np.ndarray
    y: np.ndarray
    color: RGBA
    alpha: float | None
    size: float | None
    marker: str | None
    fill: bool | None
    edgecolor: RGBA | None
    label: str | None


@dataclass(frozen=True)
class AxesScene:
    primitives: tuple[Bars | Line | Points, ...]
    title, xlabel, ylabel, xscale, yscale, xlim, ylim, background_color
    legend: LegendStyle | None  # None when no primitive has a label
    categories: tuple[str, ...] | None


@dataclass(frozen=True)
class GridScene:
    panels: tuple[AxesScene, ...]
    ncols: int
    title: str | None
```

`build_scene(spec)` is a pure function of the spec:

1. resolve the x extent of the panel: `PanelSpec.xmin`/`xmax` where set, else the union of
   `x_extent()` of the data-bound marks (3.3);
2. call `to_primitives(extent)` on each mark, in order;
3. give a color of `DEFAULT_PALETTE` (cycling, in drawing order) to each primitive whose color is
   `None`. **Every** uncolored primitive gets one, including the first of a single-mark chart
   (decision D3): today the first color is the library default, which differs per backend (F3,
   Constraint 3);
4. collect the legend: present if and only if one primitive has a label (the `series_0` names that
   `xy` invents for unlabeled stacked series disappear);
5. collect the categories of the panel in order of first appearance.

Lowering of each mark (all in `plotmux.specs`, numpy only, unit-tested with literal arrays):

| Mark             | Primitives                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `HistogramSpec`  | `Bars`: `np.histogram(values, bins, range=find_range(...), density)`; `x` = bin centers, `width` = `np.diff(edges)`, `base` = 0 |
| `BarSpec`        | `Bars`: `x`, `height=y`, `base` = 0, `width`                                                                                    |
| `StackedBarSpec` | one `Bars` per series, `base` = running total of the previous series                                                            |
| `CdfSpec`        | `Line`: the step vertices of the empirical CDF (D4); `nbins=None` is exact, an integer bins the values first                    |
| `LineSpec`       | `Line`                                                                                                                          |
| `ScatterSpec`    | `Points`                                                                                                                        |
| `SlopeSpec`      | `Line` with two endpoints, `(lo, g * lo + b)` and `(hi, g * hi + b)`, where `lo`, `hi` is the panel x extent                    |

The CDF is the empirical `P(X <= x)` over **all** the values; `xmin`/`xmax` restrict the vertices
that are drawn and do not renormalize the curve (F3, decision D4).

### 3.3 The slope: a segment everywhere, a native line where it exists

Today a standalone slope exists on `matplotlib` (`Axes.axline`) and `bokeh` (`models.Slope`) only,
and the other three need a layer and a data-bound sibling to find two endpoints (F2). The target
uses the rule that already makes the layer case work, made backend independent:

> The x extent of a panel is its explicit `xmin`/`xmax` where given, else the extent of its
> data-bound marks. A `SlopeSpec` with no extent (no `xmin`/`xmax` and no data-bound sibling) raises
> `InvalidSpecError` when the panel is built.

The lowering of a `SlopeSpec` is a `Line` with the two endpoints of the extent, so every backend can
draw it with `draw_line` and no new primitive exists. `plotmux.slope(1.0, xmin=0, xmax=10)` works on
every backend, standalone, in a layer and in a grid. The `Line` also carries
`infinite=(gradient, intercept)`, and this is an **optional optimization of `draw_line`** (decision
D2): a backend that has a native infinite line (`Axes.axline` on `matplotlib`, `models.Slope` on
`bokeh`) draws it when `infinite` is set, which keeps the line following an interactive zoom beyond
the extent; the other backends ignore the field and draw the segment. The two native lines are
two branches inside `draw_line` of their backend, not modules: the two `slope.py` modules,
`resolve_slope_xrange`, the three copies of the "no sibling" block (F11) and the `SlopeSpec` caveats
still disappear. The extent still comes from the scene, so the autoscale and the conformance test
see the same endpoints on every backend; the native line adds no data to the axes.

### 3.4 The backend contract

```python
class Backend(ABC):
    name: ClassVar[str]

    @abstractmethod
    def capabilities(self) -> BackendCapabilities: ...  # formats, legend locations, markers
    @abstractmethod
    def draw(self, scene: AxesScene | GridScene) -> Any: ...  # the native figure
    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None: ...
    def show(self, native: Any) -> None: ...  # default: NotImplementedError
    def mimebundle(self, native: Any) -> dict[str, Any] | None: ...  # default: native's own repr

    def render(self, spec: FigureSpec) -> Any:  # concrete, not overridden
        capabilities.check(spec)  # UnsupportedSpecError, before drawing
        return self.draw(build_scene(spec))
```

- A backend implements `draw`, `save`, `capabilities` and, where the library needs it, `show` and
  `mimebundle`. Inside `draw`, a function per primitive (`draw_bars`, `draw_line`, `draw_points`),
  one `apply_style(axes_scene)` and the composition of a grid. `_RENDERERS`, `_make_renderer`,
  `make_renderer`, the per-spec modules, the layer tables and `resolve_renderer` are deleted.
- **Capabilities are data**, checked by the base class before drawing:

  ```python
  @dataclass(frozen=True)
  class BackendCapabilities:
      name: str
      formats: frozenset[str]  # panels
      grid_formats: frozenset[str]  # {"html"} on xy
      legend_locations: frozenset[str]  # the portable set, minus what the library lacks
      markers: frozenset[str]
  ```

  The portable legend set drops `"best"`, which three backends cannot honor (decision D6). A value
  outside the set raises `UnsupportedSpecError` naming the backend and the supported values, so a
  silent no-op (F3) becomes an error. `Figure.supported_formats` reads it.

- **Display and show are owned by the backend** (F6). `Figure.show()` calls `backend.show(native)`
  (`bokeh.io.show`, `native.show()` for `plotly`/`altair`/`xy`, and a pyplot figure manager for
  `matplotlib`); `Figure._repr_mimebundle_` calls `backend.mimebundle(native)` (a PNG through
  `savefig` for `matplotlib`, whose `savefig` already works on a figure created without pyplot
  **[verified]**, so `attach_repr_png` and its monkeypatch are not needed). `Figure.__getattr__`,
  the dunder whitelist and the duck-typed `canvas.print_png` are deleted.
- **No keyword pass-through** (F7). `render(spec)` takes nothing else. The escape hatch is the
  native figure: `fig.to_native()` is modified by the user after the render (decision D1). The
  library-specific options that exist today only through `**kwargs` can all be applied there.

### 3.5 The registry

```python
_BUILTIN = {
    "matplotlib": "plotmux.backends.matplotlib:MatplotlibBackend",
    "xy": "plotmux.backends.xy:XyBackend",
    ...
}
```

- `get_backend(name)` looks, in this order, in the instances registered with
  `register_backend(backend, *, replace=False)`, in the built-in table, and in the entry-point group
  `plotmux.backends`; it imports **only the module of that name**, instantiates the class once and
  caches it. An `ImportError` becomes `BackendNotFoundError` with the extra to install
  (`pip install "plotmux[matplotlib]"`) and the original error as the cause.
- The entry point value is `package.module:BackendClass` (no import-time side effect). `import
plotmux` reads **no** entry point (F8): `known_backend_names()` reads their names from the
  installed metadata, which imports nothing, and `set_backend` still rejects an unknown name at the
  call site.
- A built-in name cannot be taken over by a plugin: a plugin that wants it calls
  `register_backend(..., replace=True)` explicitly (decision D7).
- The subpackages `plotmux.backends.<name>` keep only `backend.py` and `style.py`; their
  `__init__.py` no longer registers anything. The `is_*_available()` helpers of
  `plotmux.utils.imports` stay (the `CLAUDE.md` convention): the registry uses them for
  `available_backends()`.

### 3.6 `Figure`, `export`, `config`

- `Figure(spec, backend_name, native)` stays a slotted dataclass with `show()`, `save(path)`,
  `to_native()`, `supported_formats` and the two display hooks of 3.4. `spec` is a `PanelSpec` or a
  `GridSpec`.
- `export.save(figure, path)` is unchanged: sanitize the path, take the format from the suffix,
  validate it against `capabilities().formats` (or `grid_formats` for a grid) **before** creating
  the directory, then call `backend.save`.
- `config` is unchanged (`ContextVar`, `set_backend`, `backend()`), which is already right.

### 3.7 The public API

`api.py` builds specs and calls one `_render`. The repeated parameters are declared once as a
`TypedDict`, as `DESIGN.md` 9.2 proposed, and documented once:

```python
class PanelOptions(TypedDict, total=False):
    title: str | None
    xlabel: str | None
    ylabel: str | None
    xscale: Literal["linear", "log"]
    yscale: Literal["linear", "log"]
    ymin: float | None
    ymax: float | None
    background_color: Color
    legend_title: str | None
    legend_location: LegendLocation | None
    legend_orientation: Literal["vertical", "horizontal"] | None
    backend: str | None


class BoundedPanelOptions(PanelOptions, total=False):  # adds the axis limits
    xmin: float | None
    xmax: float | None


def hist(
    values,
    *,
    bins=30,
    xmin=None,
    xmax=None,
    density=False,
    label=None,
    color=None,
    alpha=None,
    **panel: Unpack[PanelOptions],
) -> Figure: ...
def line(
    x,
    y,
    *,
    label=None,
    color=None,
    alpha=None,
    linewidth=None,
    linestyle="solid",
    **panel: Unpack[BoundedPanelOptions],
) -> Figure: ...
```

`hist`/`cdf` take `PanelOptions` (their `xmin`/`xmax` are the data range, 3.1); the other charts
and `layer` take `BoundedPanelOptions`. Explicit keywords keep their autocompletion through
`Unpack`; a misspelled keyword is now a `TypeError` of `plotmux` at the call site, with the correct
signature, whatever the backend.

- `layer(*items, **panel)` accepts marks and single-panel `Figure` objects. A `Figure` contributes
  its marks. The axes fields of the call are used; where the call leaves one unset, the unique
  non-default value of the items is used; two different non-default values raise
  `InvalidSpecError` (decision D8). Today a `Figure`'s title and labels are silently dropped.
- `grid(*items, ncols=1, title=None, backend=None)` accepts panels, marks (wrapped in a default
  panel) and single-panel `Figure` objects. It exposes no axis option: each panel keeps its own.
- The nine functions stay: `hist`, `bar`, `stacked_bar`, `cdf`, `line`, `scatter`, `slope`,
  `layer`, `grid`. `slope` takes `xmin`/`xmax` (3.3).

## 4. Public API after the change

```python
# plotmux
hist, bar, stacked_bar, cdf, line, scatter, slope, layer, grid  # (see 3.7)
set_backend, backend, __version__

# plotmux.specs
(
    MarkSpec,
    HistogramSpec,
    CdfSpec,
    BarSpec,
    StackedBarSpec,
    BarSeries,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)
PanelSpec, GridSpec  # LayerSpec, BaseSpec, XBoundSpec removed

# plotmux.scene
build_scene, AxesScene, GridScene, Bars, Line, Points

# plotmux.backends
Backend, BackendCapabilities, get_backend, register_backend, capabilities, available_backends

# plotmux.figure, plotmux.export, plotmux.config, plotmux.exceptions, plotmux.colors, plotmux.utils
Figure, save, ...  # unchanged unless listed in 3
```

Removed: `LayerSpec`, `BaseSpec` (the figure fields), `XBoundSpec`, `check_equal_length` (replaced
by a validator on `MarkSpec`), the `**kwargs` of every plotting function,
`backends.base.make_renderer`, `resolve_renderer`, `check_export_format` (folded into
`capabilities`), `plotmux.utils.slope`, `plotmux.utils.cdf.compute_cdf_steps` (becomes the exact
`cdf_steps`), `Figure.__getattr__`, and the per-spec renderer modules of the five backends.

## 5. Dependents

| Dependent                       | Change                                                                                                                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/docs/uguide/*.md`         | Rewrite `api.md` (the options table once, the `xmin`/`xmax` rule of hist and cdf), `cdf.md` (exact CDF), `layer.md` (merge rule, slope in any layer), `grid.md`, `backends.md` (plugin contract), `figure.md` (`show`, capabilities). |
| `docs/docs/dev/architecture.md` | Replace the layout and the "layering and grid" sections by 3.1 to 3.5. Keep it a short summary of `DESIGN.md`.                                                                                                                        |
| `DESIGN.md`                     | Rewrite as the current-state reference, about 400 lines: sections 1 to 5 of this document, the support table, the open questions that are still open. Move sections 8, 9 and the case studies to `design_history.md`.                 |
| `docs/docs/dev/development.md`  | "Adding a new chart type" becomes "add a `MarkSpec` with `to_primitives`"; "adding a new backend" lists `draw`, `save`, `capabilities`.                                                                                               |
| `notebooks/*.ipynb`             | Re-run `backend`, `compare_backends`, `slope_example`; `slope_example` gains `xmin`/`xmax`.                                                                                                                                           |
| Third-party backends            | Contract change (3.4, 3.5): a class with `draw`/`save`/`capabilities`, referenced by an entry point `name = "pkg.module:Class"`. Listed in the release notes.                                                                         |
| `plotmux.testing.fixtures`      | No change (the `*_available` markers).                                                                                                                                                                                                |

## 6. Evidence

Probes run on `main` with the five backends installed (scripts outside the repository).
**[verified]**

| Probe                                                                  | Result on `main`                                                                                                                       |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| support matrix: 7 marks x {standalone, layer, grid} x 5 backends       | the appendix table: slope standalone on 2 backends, in a grid on 0; stacked bar in a layer or grid on 0 (error `UnsupportedSpecError`) |
| `LineSpec(x=a, y=a)` then `a[0] = 99`                                  | `spec.x[0]` is `99.0`                                                                                                                  |
| `LineSpec(...) == LineSpec(...)`; `hash(spec)`                         | `ValueError` (truth value of an array); `TypeError` (unhashable `ndarray`)                                                             |
| `plotmux.line(x, y, colour="red", backend=b)` on 5 backends            | `AttributeError`, `TypeError`, `AttributeError`, `SchemaValidationError`, `ValueError`; none names `plotmux`                           |
| `LineSpec(title="child", yscale="log")` inside a `LayerSpec`           | accepted, kept in `layers[0]`, not applied                                                                                             |
| `plotmux.line(...).show()` on `matplotlib`, `bokeh`                    | `AttributeError: Figure.show works only for figures managed by pyplot`; `NotImplementedError`                                          |
| `Figure()` of matplotlib without pyplot: `fig.savefig(BytesIO, "png")` | works (a PNG is produced), so the monkeypatched `_repr_png_` is unnecessary for the display                                            |
| `find_range([1, 2, nan, 3])`; `np.histogram([1, 2, nan, 3], bins=2)`   | `(1.0, 3.0)`; `ValueError: autodetected range of [nan, nan] is not finite`                                                             |
| Vega-Lite bar with `x`, `x2`, `y`, `y2` (altair 6)                     | `Chart.to_dict()` validates; this is the encoding of `Bars` with an array width and a base (3.2). Rendering is not checked.            |
| render time, 1,000,000 values / 100,000 points                         | `hist` 8 to 17 ms and `cdf` 7 to 17 ms on all five; `line` 100,000 points: `altair` 3,421 ms, others 0 to 5 ms (F12)                   |

Not verified, and gated in section 8: that `xy.bar` with an array `width` and a `base` draws the
same bars as the others (the signature accepts both); that Vega-Lite accepts the SVG path shape for
a cross; that the `bokeh` `vbar` honors an array `width`; that `Unpack[TypedDict]` is accepted by
the pinned `ty` and `pyright`.

## 7. Changes to reach the target state

One branch and one pull request per step (`CLAUDE.md`). Steps 1 to 5 are independent and each one is
releasable. Steps 6 to 9 are a **stack** (each branch from the previous one): `main` must not hold a
half-ported backend, so the stack is merged once its last step is green; its steps are reviewed
one at a time.

| Step | Change                                                                                                                                                                                                                                                                                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | **Fix the documentation (F13).** Five backends everywhere, remove the stale matplotlib question, split `DESIGN.md` into the current-state reference and the history. No code.                                                                                                                                                        |
| 2    | **Immutable specs (F5).** Copy arrays and make them read-only in `__post_init__`, add `Spec.__eq__`, set `eq=False`. Regression tests that fail without the change.                                                                                                                                                                  |
| 3    | **`Figure.show` and display (F6).** `Backend.show` and `Backend.mimebundle`, port the five backends, delete `Figure.__getattr__` and `attach_repr_png`. Regression test: `show()` on every backend under a non-interactive configuration.                                                                                            |
| 4    | **Lazy registry and plugin contract (F8).** Built-in table of `module:Class` strings, entry points by name and loaded on demand, `register_backend(replace=)`, `available_backends()`. Test that `import plotmux` imports no backend and no entry point.                                                                             |
| 5    | **Input policy (F10).** Decision D5 in the specs, with the table of cases in the docs and one parametrized test per case. Can be merged into step 6 if D5 is changed.                                                                                                                                                                |
| 6    | **Core model (F1, F4, F11).** `MarkSpec`, `PanelSpec`, `GridSpec`, the three primitives, `build_scene` and the lowering of every mark, the exact CDF, the rewritten `api.py` with `PanelOptions`. Old backends are not touched yet: a temporary adapter in `Backend.render` is **not** added; the stack is not merged before step 9. |
| 7    | **Port `matplotlib` and `xy`.** `draw`, `style`, `capabilities`, `save`; delete the per-spec modules. The conformance harness (section 8) lands with the first one.                                                                                                                                                                  |
| 8    | **Port `bokeh`, `altair` and `plotly`.** Includes the `x`/`x2` bars and the cross marker of `altair`, and the data path of `altair` (F12).                                                                                                                                                                                           |
| 9    | **Delete what is left** (`LayerSpec`, `XBoundSpec`, `resolve_slope_xrange`, `make_renderer`, `**kwargs`), rewrite `BackendCapabilities`, run the full gates.                                                                                                                                                                         |
| 10   | **Documentation and notebooks.** The guides, `DESIGN.md`, `architecture.md`, `development.md`, the notebooks, and the migration page for the release notes.                                                                                                                                                                          |

## 8. Tests and gates

Unit tests mirror the source tree (`tests/unit/`); the conventions of `CLAUDE.md` apply (one
behaviour per test, literal expected values, a regression test for every bug, no local imports,
integration tests for everything that is patched).

- **Lowering** (`tests/unit/specs/test_<mark>.py`): `to_primitives` of every mark returns the whole
  primitive tuple asserted against a literal (centers, widths, base, color), for the typical case, a
  single value, an empty-looking case, explicit and quantile ranges, a categorical `x`.
- **Scene** (`tests/unit/test_scene.py`): palette assignment and cycling, an explicit color does not
  consume a slot, the legend exists if and only if a label exists, the categories in order, the
  extent rule of 3.3 (explicit limits, siblings, none: `InvalidSpecError`), mixing categorical and
  numeric marks raises.
- **Specs**: immutability (the caller's array is not aliased, `spec.x[0] = 1` raises), equality
  (equal, different values, different types), the input policy table (D5) one case per test.
- **Conformance, the test of the property "same chart everywhere"**
  (`tests/integration/conformance/`): for each backend an `extract(native)` returns the drawn
  primitives from the native object (the `Line2D` data and `Rectangle` patches of `matplotlib`, the
  glyph data sources of `bokeh`, the traces of `plotly`, the inline data and encodings of `altair`,
  the marks of `xy`). A parametrized test over **7 marks x {standalone, layer, grid} x 5 backends**
  checks that nothing raises and that `extract(render(spec))` equals `build_scene(spec).primitives`
  within a tolerance. This is the support matrix of the appendix, executable; it replaces the
  `_CAVEATS` strings.
- **Backend contract**: the capability checks (a legend location or marker outside the set raises
  `UnsupportedSpecError` before drawing; an export format outside the set raises
  `UnsupportedFormatError` before the directory is created); `show` and `mimebundle` per backend; a
  minimal fake backend registered with `register_backend` and drawn through the contract.
- **Registry**: `import plotmux` in a subprocess imports no module of `plotmux.backends.<name>`, no
  plotting library and no entry point; an entry point is loaded on first use of its name; a missing
  library gives `BackendNotFoundError` with the extra; a plugin cannot replace a built-in without
  `replace=True`.
- **API**: a misspelled keyword is a `TypeError` naming the function; `layer` merge rule (unique
  value, conflict, explicit call argument wins); `grid` of marks, panels and figures.
- **Types**: `ty check` and `pyright` pass on `api.py` with `Unpack[PanelOptions]` (gate: if the
  pinned versions reject it, the fallback is explicit keywords generated by the docstring helper
  that exists today).
- **Performance**: `build_scene` for a histogram of 1,000,000 values and an exact CDF of 100,000
  values; the render of the probe of section 6 on each backend must not be slower than `main` (the
  numbers of the table of section 6), and the `altair` line of 100,000 points must be reported
  (target: no worse, expected: better).
- **Size**: the table of the appendix is re-measured after step 9; a result larger than `main`
  rejects the design (Constraint 5).
- Coverage: 100 % of the code added or changed (`--cov=plotmux`), no `# pragma: no cover`;
  doctests of every public function and of the guides.

## 9. Decisions for the maintainers

**D1. Remove the `**kwargs` pass-through?** _Recommended: yes._ It makes a call backend specific
(F7), forwards to the mark and not to the figure, and turns a typo into a deep library error. The
escape hatch is `to_native()`. Alternative: keep one explicit `backend_options: Mapping` applied to
the native figure after the render, with its own documentation per backend; more code, and it
reintroduces the problem for the options it carries.

**D2. Draw a slope as a segment on every backend?** _Decided: no, keep the two native primitives as
an optional optimization of `draw_line`._ The core lowers a slope to a `Line` with two endpoints (so
the rule is one, in a layer and in a grid, with no caveat) and marks it with `infinite`;
`matplotlib` (`Axes.axline`) and `bokeh` (`models.Slope`) draw the native line, which keeps the
interactivity (the line extends when the user zooms past the extent), and `xy`, `plotly` and
`altair` draw the segment. The cost: two special cases inside `draw_line`, and a conformance test
that must compare the endpoints of the scene and not the data of the native infinite line on these
two backends. Alternative (the first recommendation): the segment on every backend, no special case,
no zoom beyond the extent.

**D3. Always assign a palette color?** _Recommended: yes._ The first color of a single chart is
`PRIMARY` on every backend instead of the library default, so the swap does not change the color
(Constraint 3, F3). Alternative: keep `None` for a single mark; the colors of a single chart then
differ per backend.

**D4. An exact empirical CDF, not renormalized by the range?** _Recommended: yes._ `CdfSpec` is the
empirical CDF: the vertices are the sorted values, `nbins` is an opt-in binning for large inputs,
and `xmin`/`xmax` restrict what is drawn without changing `P(X <= x)`. Today `nbins=None` means 10
bins on one backend and 100 on two others, and a range renormalizes the curve (F3). Alternative:
keep the binned CDF with a single default of 100 bins in the core; simpler to port, still an
approximation with an arbitrary default.

**D5. Policy for `NaN` and `inf`.** _Recommended:_ `HistogramSpec` and `CdfSpec` drop `NaN` and
`inf` (documented) and raise `InvalidSpecError` if no finite value is left; `LineSpec` and
`ScatterSpec` keep `NaN` (a gap in a line, no point) and reject `inf`; the quantile and the range
use the finite values. **When values are dropped, the spec emits a `UserWarning` that says that a
`NaN` or `inf` was detected and filtered out, with the count** (once per spec, at construction, so
it is not repeated on each render or backend swap); a test per case checks the warning and its
message. A `NaN` kept in a line or a scatter is intended and does not warn. Alternative: reject
every non-finite value in every spec (strictest, and breaks a line with gaps); or drop silently
(no warning, as today).

**D6. Drop `legend_location="best"`?** _Recommended: yes._ It is not portable (three backends have
no automatic placement) and is a silent no-op there today (F3). `None` means the library default,
which is automatic placement where it exists. Alternative: keep it and make it an error on the three
backends, which makes the portable set backend dependent.

**D7. Who wins on a backend name?** _Recommended:_ explicit `register_backend(..., replace=True)`
over a built-in over an entry point. A plugin cannot take over `matplotlib` by being installed
(today the last registration wins, F8). Alternative: let the entry point win, as the architecture
page describes for plugins today; convenient for a patched backend, and a surprise for a package
that happens to be installed.

**D8. Merging the axes fields of the figures given to `layer`.** _Recommended:_ the call arguments
win, else the unique non-default value of the items, else `InvalidSpecError` on a conflict.
Alternative: ignore the axes fields of the items, as today (silent loss, F1), or forbid them
(`layer` then accepts marks only, and `layer(fig1, fig2)` is removed).

**D9. Keep the names `HistogramSpec`, `LineSpec`, ... for the marks?** _Recommended: yes._ They are
the names users and the guides know; only the figure-level fields move. Alternative: rename to
`Histogram`, `Line`, ... (shorter, and no confusion with `PanelSpec`) at the price of every import.

**D10. Where does the lowering live?** _Recommended: as `MarkSpec.to_primitives`._ One method per
mark, next to its validation, and a new chart type is one class. Alternative: a `singledispatch`
function in `plotmux.scene` keeps the specs free of numpy computation, and adds a second place to
edit for each chart type.

## 10. Not covered

- **Figure size, DPI, theme and fonts.** No unified option exists today either (`**kwargs` cannot
  reach the figure, F7); `to_native()` is the way. A `size=(width, height)` option is the natural
  next addition and is a separate design.
- **New chart types** (box plot, heat map, error bars, area). The design makes a box plot a
  composition of `Bars` and `Line`; whether it is generic enough is the open question of
  `DESIGN.md` section 7, left as it is.
- **Secondary axes, annotations, subplots sharing axes, dates on an axis.** Out of scope, as today.
- **Stacked bars with negative values.** The running total is a plain cumulative sum, as today.
- **A sixth backend** (`plotnine`): follows the new contract; not part of this change.
- **Static export for `bokeh`, `altair`, `plotly`**: unchanged; the optional exporters stay the
  user's choice.
- **The `altair` performance** (F12): the cause is diagnosed in step 8, not here.

## Appendix: support matrix on `main`

Probe on `main`: each mark standalone, in a layer with a `LineSpec` sibling, and as the single cell
of a grid; `Y` means no exception. **[verified]**

| Mark                          | Standalone                                     | In a layer                        | In a grid   |
| ----------------------------- | ---------------------------------------------- | --------------------------------- | ----------- |
| hist, cdf, line, scatter, bar | `matplotlib` `xy` `bokeh` `altair` `plotly`: Y | all five: Y                       | all five: Y |
| stacked bar                   | all five: Y                                    | **none**                          | **none**    |
| slope                         | `matplotlib` and `bokeh` only                  | all five: Y (with a data sibling) | **none**    |
| a layer in a grid             | -                                              | -                                 | all five: Y |

In the target, every cell of this table is `Y` on every backend (section 8, conformance test).

## Appendix: effect on the size of the package

Estimates from the current code and from the design; the gate is the measure after step 9
(section 8, Size), not these numbers. The backend rows exclude docstrings, comments and blank lines;
the rows marked "with docstrings" include them.

| Part                              | Lines today             | Expected after               | Why                                                                                                                       |
| --------------------------------- | ----------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `backends/<name>/` (each of five) | 268 to 339 (12 modules) | about 150 to 220 (2 modules) | `draw_bars`, `draw_line`, `draw_points`, `apply_style`, grid, `save`; no per-spec module, no layer table, no slope module |
| `backends/base.py`, `registry.py` | 436 (with docstrings)   | about 330 (with docstrings)  | no `make_renderer`, `resolve_renderer`, `_RENDERERS`; lazy table instead of eager registration and plugin import          |
| `specs/` (with the validation)    | 1,221 (with docstrings) | about 750 (with docstrings)  | the alpha, label, color, length and axes checks once; no `LayerSpec`, `XBoundSpec`, shadowed fields                       |
| `scene.py`, primitives            | 0                       | about 250                    | new: the lowering of seven marks (numpy), the palette, the extent, the legend                                             |
| `api.py`                          | 849 (with docstrings)   | about 350 (with docstrings)  | `PanelOptions` declared once                                                                                              |
| `figure.py`                       | 176 (with docstrings)   | about 100 (with docstrings)  | no `__getattr__`, no whitelist, no duck-typed PNG                                                                         |
| `utils/slope.py`                  | 76 (with docstrings)    | 0                            | the extent rule lives in the scene                                                                                        |

The tests grow where the new properties need them (conformance, registry, policy) and shrink where
five backends repeated the same per-spec tests; the count today is 1,146 tests in 124 files.
