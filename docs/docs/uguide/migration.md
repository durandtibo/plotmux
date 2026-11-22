# Migrating to the Primitives-Based Design

:book: This page lists the breaking changes of the core-model redesign (see
[`DESIGN.md`](https://github.com/durandtibo/plotmux/blob/main/DESIGN.md)) and how to update your
code. It is the source of the migration section of the release notes. There is no alias, no
deprecation period and no shim: the old names are gone.

The short version: **a spec is now a mark plus a panel.** The figure-level fields (title, labels,
scales, limits, background, legend) moved from every chart spec to `PanelSpec`, a layer is a panel
with several marks, and a backend only draws three primitives.

## Using the Plotting Functions

The nine functions keep their names and their arguments. Five things change:

| Before                                                                                                   | After                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plotmux.hist(x, histtype="step")`: extra keywords go to the library                                     | A `TypeError` of `plotmux`: `hist() got an unexpected keyword argument 'histtype'`. Modify the native figure with `fig.to_native()` instead.            |
| `xmin`/`xmax` of `hist`/`cdf` were documented as the x-axis range (and set the limits of a CDF)          | `xmin`/`xmax` of `hist` and `cdf` are the range of the data; they are not axis limits. Use `xmin`/`xmax` of `line`, `bar`, ... or of `layer` for limits |
| `plotmux.cdf(x)`: a binned CDF (10 or 100 bins, depending on the backend), renormalized by `xmin`/`xmax` | The exact empirical `P(X <= x)`; `nbins` is an opt-in binning; `xmin`/`xmax` cut the curve without renormalizing it                                     |
| `plotmux.slope(2, 1)` standalone on `matplotlib` and `bokeh` only                                        | `plotmux.slope(2, 1, xmin=0, xmax=10)` on every backend; a slope needs an x extent                                                                      |
| `legend_location="best"`                                                                                 | Removed: three backends have no automatic placement. Use `None` for the default of the library                                                          |

Also:

- The first color of a chart is now the first color of `DEFAULT_PALETTE` on every backend (it was the
  default color of the library).
- `layer(...)` merges the axes options of the figures it is given (see
  [Layering Charts](layer.md)): the title and the labels of a figure used to be dropped silently.
  Two figures with different non-default values of an option now raise an `InvalidSpecError`; set the
  option in the call to `layer`.
- `stacked_bar` works in a layer and in a grid, and `slope` in a grid, on every backend.
- `legend_title`, `legend_location` and `legend_orientation` are now keyword arguments of every
  plotting function (they were only fields of the specs).
- `fig.supported_formats` of a grid reads the formats of the grid (`html` only for `xy`).
- A format that a backend does not support raises an `UnsupportedFormatError` before any file or
  directory is created.

## Using the Specs

| Before                                                              | After                                                                                |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `HistogramSpec(values=v, title="t", xscale="log")`                  | `PanelSpec(marks=(HistogramSpec(values=v),), title="t", xscale="log")`               |
| `LayerSpec(layers=(a, b), title="t")`                               | `PanelSpec(marks=(a, b), title="t")`; a layer is a panel with several marks          |
| `GridSpec(cells=(a, b), ncols=2)` where a cell is a spec or a layer | `GridSpec(panels=(PanelSpec(marks=(a,)), PanelSpec(marks=(b,))), ncols=2)`           |
| `BaseSpec`, `XBoundSpec`                                            | `MarkSpec` (label, color, alpha) and `PanelSpec` (the axes style and the limits)     |
| `fig.spec` is the spec that was rendered                            | `fig.spec` is a `PanelSpec` or a `GridSpec`; the marks are in `fig.spec.marks`       |
| `StackedBarSpec(..., label=..., color=...)`                         | The label and the color are set on each `BarSeries`; setting them on the spec raises |
| `CdfSpec(..., ylabel=...)` (the default `"cumulative probability"`) | The default is set by `plotmux.cdf`; a `PanelSpec` has `ylabel=None` by default      |
| Specs compared by identity, arrays aliased                          | Specs are immutable and compare by value; arrays are copied and read-only            |
| `plotmux.specs.check_equal_length`                                  | `plotmux.utils.to_paired_arrays`                                                     |
| `plotmux.utils.compute_cdf_steps`                                   | `plotmux.utils.cdf_steps` (exact CDF)                                                |
| `plotmux.utils.slope.resolve_slope_xrange`                          | Removed: the x extent is `PanelSpec.x_extent()`                                      |

## Writing a Backend

The contract of a third-party backend changed (see
[Adding a Third-Party Backend](backends.md#adding-a-third-party-backend)).

| Before                                                                 | After                                                                                                       |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `render(spec, **kwargs)` dispatched on the type of the spec            | `draw(scene)`: draw `Bars`, `Line` and `Points`, and apply the axes style; `render` is concrete             |
| `supported_formats`, `_RENDERERS` and `_CAVEATS` class attributes      | `capabilities()` returns a `BackendCapabilities` (`formats`, `grid_formats`, `legend_locations`, `markers`) |
| `make_renderer`, `resolve_renderer`, `check_export_format`             | Removed: the base class checks the scene and `export.save` checks the format                                |
| A module per spec type, per layer and per grid                         | `backend.py` and `style.py`                                                                                 |
| The entry point value was a module that registered a backend at import | The value is `package.module:BackendClass`; there is no import-time side effect                             |
| A new chart type needed a renderer in every backend                    | A new chart type is a `MarkSpec` with `to_primitives`, with no backend change                               |

## Checking What a Backend Supports

`plotmux.backends.capabilities(name)` returns the formats, the legend locations and the markers of a
backend. The old `spec_types` and `caveats` are gone: every chart type works standalone, in a layer
and in a grid on every backend.
