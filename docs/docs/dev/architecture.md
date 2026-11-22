# Architecture

This page describes `plotmux`'s internal architecture: how it is organized, and why. It is a short
summary of [DESIGN.md](https://github.com/durandtibo/plotmux/blob/main/DESIGN.md) in the
repository, the current-state design reference.

## Goal

`plotmux` is a lightweight abstraction layer over Python's plotting libraries: users write plotting
code once against `plotmux`'s unified API and choose the rendering backend (`matplotlib`, `xy`,
`bokeh`, `altair`, `plotly`, ...) at runtime. Swapping backends is a one-line configuration change,
and adding a new backend or chart type does not require changing existing code.

The unified API targets a small set of generic, broadly useful chart types and figure-level
concerns: histograms, empirical CDFs, line charts, scatter plots, bar charts (plain and stacked),
slope/abline lines, layering them together, laying them out in a grid, common axes styling,
per-mark color, export. A niche or highly backend-specific plot stays behind the escape hatch
(`Figure.to_native()`) rather than becoming a new spec.

## Principle: Specs Are Plain Data, the Core Lowers Them, a Backend Draws Primitives

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

The core owns every decision that changes the numbers on the screen: the range and the bins of a
histogram, the steps of a CDF, the stacking of a bar chart, the default colors, the x extent of a
panel. A backend owns only the translation of three primitives and of the axes style into one
library. So the same spec draws the same numbers on every backend, and a backend cannot draw a
different histogram.

Rules that follow:

- A spec never holds a plotting-library object, and importing `plotmux.specs` imports no plotting
  library.
- Backends are optional and lazy: `import plotmux` imports no backend, no plotting library and no
  plugin. The core depends only on `coola` and `numpy`.
- Nothing outside a `backends/<name>/` subpackage special-cases a backend by name.

## Package Layout

```text
src/plotmux/
├── utils/
│   ├── range.py                  # find_range(), check_range_bounds(): quantile-or-explicit ranges
│   ├── cdf.py                    # cdf_steps(): exact (or binned) empirical CDF step vertices
│   ├── categorical.py            # is_categorical(): string-vs-numeric x-axis check
│   ├── array.py                  # to_readonly_array(), to_paired_arrays()
│   ├── extent.py                 # finite_extent()
│   ├── finite.py                 # the NaN/inf policy: drop_non_finite(), check_no_inf()
│   ├── equality.py               # ValueObject: value equality for the frozen dataclasses
│   └── imports/                  # one module per optional backend dependency
├── colors/
│   ├── parser.py                 # parse_color(), parse_optional_color(): canonical RGBA
│   ├── palette.py                # PRIMARY/SECONDARY/TERTIARY, DEFAULT_PALETTE
│   └── named.py                  # static CSS/matplotlib named-color table
├── specs/
│   ├── base.py                   # Spec (immutable value object), MarkSpec (label/color/alpha,
│   │                             #   x_extent(), to_primitives())
│   ├── panel.py                  # PanelSpec: marks + axes style (title, labels, scales, limits,
│   │                             #   background, legend)
│   ├── grid.py                   # GridSpec: independent panels
│   ├── histogram.py cdf.py bar.py stacked_bar.py line.py scatter.py slope.py   # the marks
├── primitives.py                 # Bars, Line, Points
├── scene.py                      # build_scene(), AxesScene, GridScene, LegendStyle
├── backends/
│   ├── base.py                   # Backend ABC + BackendCapabilities
│   ├── registry.py               # register_backend() / get_backend() / entry points
│   └── <name>/                   # matplotlib, xy, bokeh, altair, plotly:
│       ├── backend.py            #   the Backend, draw_bars/draw_line/draw_points, the grid, save
│       └── style.py              #   the axes style and the translation tables
├── figure.py                     # Figure wrapper
├── export.py                     # save(figure, path)
├── config.py                     # default backend (a ContextVar) + context manager
├── exceptions.py                 # PlotmuxError hierarchy
├── api.py                        # hist(), bar(), stacked_bar(), cdf(), line(), scatter(),
│                                 #   slope(), layer(), grid(); PanelOptions
└── testing/fixtures.py           # pytest markers for downstream users
```

A new backend adds a `backends/<name>/` subpackage with two modules. A new chart type is one
`MarkSpec` subclass (see the [developer guide](development.md)).

## Data Flow

```text
user code
   │  plotmux.hist(values, bins=30, xmin="q0.1")
   ▼
api.py             checks the keywords, builds a HistogramSpec, wraps it in a PanelSpec,
                   resolves the active backend (explicit `backend=` > the default of config.py)
   ▼
backends.get_backend(name)   imports the module of that backend on the first use
   ▼
Backend.render(spec)         build_scene(spec) -> capabilities().check(scene) -> draw(scene)
   ▼
Figure(spec, backend_name, native)
```

`Figure.save(path)` goes through `export.save`, which takes the format from the suffix, validates it
against the capabilities of the backend (for a single panel or for a grid) before it creates any
directory, then calls `Backend.save`.

## Key Components

### Marks, Panels and Grids

- A **mark** (`MarkSpec`) is what is drawn: the data and the style of one chart type. `label`,
  `color` and `alpha` are declared and validated once. A mark knows its `x_extent()` and lowers
  itself with `to_primitives(extent)`.
- A **panel** (`PanelSpec`) is one axes: a tuple of marks and the axes style. A **layer** is a panel
  with several marks. A **grid** (`GridSpec`) is a tuple of panels. The type forbids a grid in a grid
  and a layer in a layer, and a grid of layers needs no special case.
- Specs are frozen, their arrays are copied and read-only, and they have value equality (they are
  not hashable). Every invalid input raises an `InvalidSpecError` when the spec is built.

### Primitives and the Scene

`Bars` (histogram, bar, one series of a stacked bar), `Line` (line, CDF steps, slope) and `Points`
(scatter) are the only things a backend draws. `build_scene` resolves the x extent of each panel,
lowers each mark, gives a palette color to each uncolored primitive, decides whether there is a
legend and collects the categories. The slope is a `Line` with the two endpoints of the x extent and
the `(gradient, intercept)` in `Line.infinite`, which `matplotlib` and `bokeh` use to draw a native
infinite line.

### `Backend`, `BackendCapabilities` and the Registry

A backend implements `capabilities()`, `draw(scene)` and `save()`, and where its library needs it
`show()` and `mimebundle()`. `render` is concrete. `BackendCapabilities` is data (export formats of
a figure and of a grid, legend locations, markers) that the base class checks before any drawing.
`plotmux.backends.registry` finds a backend by name (a registered instance, the built-in table, then
the entry-point group), imports only the module of that name, and turns a missing library into a
`BackendNotFoundError` with the extra to install.

### Color Parsing

`plotmux.colors.parse_color` normalizes hex strings, CSS/matplotlib named colors and RGB(A) tuples to
one RGBA tuple, from a bundled table (no matplotlib import). The scene gives the default palette
color; each backend converts the tuple to its native format.

### `plotmux.exceptions`

Every exception is a `PlotmuxError` and also its builtin counterpart, so existing `except
ValueError` code keeps working: `InvalidSpecError` and `InvalidColorError` (`ValueError`),
`UnsupportedSpecError` (`NotImplementedError`), `UnsupportedFormatError` and `ExportError`
(`ValueError`), `BackendNotFoundError` (`RuntimeError`) and `BackendRegistrationError`
(`ValueError`).

### `Figure` and `config`

`Figure(spec, backend_name, native)` keeps what was rendered, and offers `show()`, `save()`,
`to_native()` (the escape hatch to the library), `supported_formats` and the Jupyter display hook.
`config` keeps the default backend in a `ContextVar`, so it is thread and task local.

## Constraints From the Existing Codebase

- `coola` is a dependency; the optional-dependency pattern of `plotmux.utils.imports` (an
  `is_*_available` helper per library) is reused for the backends.
- `matplotlib`, `xy`, `bokeh`, `altair` and `plotly` are optional extras of `pyproject.toml`. Only
  `numpy` and `coola` are hard dependencies.
- Style conventions: `from __future__ import annotations`, explicit `__all__`, Google-style
  docstrings with runnable `pycon` examples, `ruff`/`ty`/`pyright` clean, tests split into
  `tests/unit/` (mirroring `src/plotmux/`) and `tests/integration/` (real libraries, the conformance
  test).

## What's Next

- [Development](development.md): how to add a chart type or a backend
- [DESIGN.md](https://github.com/durandtibo/plotmux/blob/main/DESIGN.md): the full design reference
