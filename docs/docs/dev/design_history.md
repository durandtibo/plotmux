# plotmux design history

This file is the historical companion to
[`DESIGN.md`](../../../DESIGN.md) (repo root): `DESIGN.md` is kept as
the current-state architecture reference (see its own §9.5 for why),
while this file keeps the chronological record of how it got there --
the case studies that drove each round of gap-closing, and the
cumulative status log each one produced. Nothing here describes
open work; every gap below is closed unless the entry says otherwise.
For what's still open, see `DESIGN.md`'s own "Open questions" and
"Candidate future work" sections.

## Cumulative status log

Core abstraction, eight chart specs (histogram, cdf, line, scatter,
bar, slope, layer, grid), five backends (matplotlib, xy, bokeh,
altair, plotly), per-mark color, common axis styling, layering, grid
layout, a `plotmux.exceptions` hierarchy, export, a predefined-colors
package, lazy per-backend imports, and a third-party backend plugin
mechanism are all in place. `SlopeSpec` is registered as a standalone
spec (`plotmux.slope(...)`) only on matplotlib and bokeh, the two
backends with a native "line by slope, independent of data range"
primitive; on altair, xy, and plotly it is supported only as a
`layer()` child alongside a data-bound sibling (see
[Case study: reproducing bokeh's slope example](#case-study-reproducing-bokehs-slope-example)),
since those three backends need concrete endpoints, not a
slope/intercept pair, and a standalone `SlopeSpec` has no data of its
own to derive endpoints from. `plotmux.slope(...)`/a slope-only
`layer()` still raise `UnsupportedSpecError` on those three backends.
All of the slope case study's gaps (per-mark alpha, separate marker
edge color, `LineSpec` `linewidth`/`linestyle`, figure background
color, explicit `ymin`/`ymax` axis bounds, and altair/xy support for
`SlopeSpec` as a layer child) are now closed; bokeh's own slope
example is reproducible, unchanged, on all five backends (modulo the
standalone-vs-layered `SlopeSpec` distinction on altair/xy/plotly
noted above). A fifth backend, plotly, has since been added, following
the same `layer()`-only treatment for `SlopeSpec` as altair/xy, for
the same reason: no native "line by slope, independent of data range"
primitive (see `plotmux.backends.plotly.slope`). Checked against
bokeh's own legend example (see
[Case study: reproducing bokeh's legend example](#case-study-reproducing-bokehs-legend-example)):
mostly reproducible unchanged (auto-generated legends from `label`, a
scatter+line pair sharing one label merging into one legend entry,
dashed-line styling, a two-panel grid), and two gaps found there -- a
legend title distinct from the figure title, and scatter marker shape
(e.g. square vs. circle) -- are now closed too (a claimed
"hollow-vs-filled fill control via `edgecolor`" close from the first
pass through that case study turned out to be bokeh-only behavior, not
a real cross-backend fix, and was corrected). Checked against bokeh's
own log plot example next (see
[Case study: reproducing bokeh's log plot example](#case-study-reproducing-bokehs-log-plot-example)):
mostly reproducible unchanged (log y-axis with explicit bounds, figure
background color, labeled dashed/dotted lines, line+scatter legend
merges), and three more gaps found there -- explicit x-axis bounds
(`xmin`/`xmax` at the `BaseSpec` level, distinct from
`HistogramSpec`/`CdfSpec`'s existing quantile-capable `xmin`/`xmax`),
legend position, and a portable hollow (no-fill) marker -- are now
closed too. Checked against bokeh's own stacked bar example next (see
[Case study: reproducing bokeh's stacked bar example](#case-study-reproducing-bokehs-stacked-bar-example)):
the first case study *not* close to reproducible -- no stacking
mechanism exists at all (`layer()`'s `BarSpec` support overlaps bars
rather than stacking them), `BarSpec`'s categorical (string) x-axis
support is inconsistent across backends (works on matplotlib/plotly,
broken on bokeh and altair, unverified on xy), and legend orientation
is a third missing legend-chrome field alongside
`legend_title`/`legend_location`; hover tooltips and fine-grained
chrome cosmetics are deliberately left as escape-hatch, non-goal
territory rather than gaps.

## Case study: reproducing bokeh's slope example

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
  alpha=None)`. Standalone (`plotmux.slope(...)`), it is matplotlib
  (`Axes.axline`) and bokeh (`fig.add_layout(bokeh.models.Slope(...))`)
  only, each with a native "line by slope, independent of data range"
  primitive matched almost one-to-one by `SlopeSpec`'s fields. altair
  and xy have neither: a standalone `SlopeSpec` has no data of its own
  to derive concrete endpoints from, and drawing between two arbitrary
  far-apart points would blow out altair's own default autoscale (xy
  has the same problem, plus no way to read back whatever range it
  picked). As a `layer()` child on those two backends, though,
  `SlopeSpec` *is* supported:
  `plotmux.backends.altair.layer.render_layer`/
  `plotmux.backends.xy.layer.render_layer` compute the x-range spanned
  by the `SlopeSpec`'s data-bound siblings
  (`plotmux.utils.slope.resolve_slope_xrange`, reading each sibling's
  `x` array, or a `HistogramSpec`/`CdfSpec`'s `find_range`-resolved
  bound) and pass it to a `layer()`-only `render_slope(spec, xrange)`
  (registered in each backend's own `layer.py`, not the backend's
  top-level `_RENDERERS`), which draws a plain two-point line spanning
  exactly that range -- exact, not an approximation, since the range
  comes from the real sibling data. A `layer()` call with no data-bound
  sibling (e.g. two `SlopeSpec`s alone) still raises
  `UnsupportedSpecError` on altair/xy, since there is nothing to derive
  a range from; this is the one respect in which `SlopeSpec` support
  is narrower on altair/xy than on matplotlib/bokeh, an unavoidable
  consequence of those two backends having no slope-by-itself
  primitive at all, not a remaining gap.
- **Separate marker fill/edge color.** `ScatterSpec.edgecolor`, an
  optional second color field normalized through the same
  `_normalize_color` machinery as `color`; `None` (the default) uses
  `color` for the edge too, so every existing single-color
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
  `BaseSpec`, mirroring how `color` itself is placed per spec, since
  `alpha` is a mark-level concern that has no meaning on
  `LayerSpec`/`GridSpec`. matplotlib: `alpha` passthrough (`None` is
  matplotlib's own "fully opaque" default, so it needs no
  special-casing); bokeh: each glyph's `alpha` (sets both
  `fill_alpha`/`line_alpha`) -- unlike matplotlib, bokeh's `alpha`
  property rejects `None` outright, so it is only added to the call
  when explicitly set (same pattern `SlopeSpec.linewidth` already
  used, see `plotmux.backends.bokeh.slope`); altair: `opacity`; xy:
  `opacity`.
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
  `find_range`'s quantile-or-explicit convention), these are
  `float | None` only -- an explicit value, no quantile-string form --
  since they are figure-level (every chart type has a y-axis; not
  every chart type has one data array to resolve a quantile against
  the way `HistogramSpec`/`CdfSpec` do). Applied post-hoc in
  `apply_common_style`, after the mark is drawn: matplotlib
  `Axes.set_ylim`; bokeh `figure.y_range.start`/`.end` (pinned
  individually on the default auto-fitting `DataRange1d`, so setting
  just one bound leaves the other autoscaled -- this is also what
  makes bokeh's `CdfSpec` renderer's own hardcoded `y_range =
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
the same `layer()` call to supply a range, which the bokeh example's
own structure (a scatter plus a reference line, layered) already
satisfies.

## Case study: reproducing bokeh's legend example

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
  `label` field already maps onto bokeh's `legend_label`, matplotlib's
  `ax.legend()`-collected artist label, altair's `label:N` color
  encoding, and plotly's `showlegend=True` -- no gap.
- **A scatter and a line sharing one label merging into a single
  legend entry.** Already correct on every backend once both children
  are drawn via one `layer()` call: matplotlib's `Axes.legend()`
  dedupes by artist label the same way bokeh's own `legend_label`
  matching does; altair's shared `label:N` encoding and plotly's
  shared `name` behave the same way -- no gap, no extra mechanism
  needed.
- **Dashed line, line width.** Already closed by the slope case
  study's `LineSpec.linewidth`/`linestyle`.
- **Hollow (no-fill) marker via `ScatterSpec.edgecolor`.** Partially
  wrong when first checked here: `edgecolor` only adds a *second*,
  separate edge color on top of whatever fills the marker -- it does
  not make the fill transparent. `spec.color=None` +
  `edgecolor=<green>` happens to *look* hollow on bokeh only, because
  bokeh's own `fill_color=None` (what `color=None` forwards to, see
  `plotmux.backends.bokeh.scatter.render_scatter`) is bokeh's native
  "transparent fill" value; on matplotlib/altair/plotly/xy, `color=None`
  instead falls back to that library's own default *opaque* fill, so
  the same spec renders filled everywhere but bokeh. This was folded
  into the "no-fill marker" gap identified in the log plot case study,
  closed there by `ScatterSpec.fill`.
- **Two figures side by side.** Already `plotmux.grid(fig1_spec,
  fig2_spec, ncols=2)`.

Two gaps were found, both new (not raised by the slope case study).
Both are now closed:

- **Legend title.** Bokeh's `p.legend.title = "Markers"` sets a
  heading on the legend box itself, independent of the figure title.
  plotmux had no equivalent field anywhere: `BaseSpec` has `title`
  (the figure/axes title) but nothing for the legend specifically, so
  there was no way to reproduce `p1.legend.title = 'Markers'`/
  `p2.legend.title = 'Lines'`. Closed by a `BaseSpec`-level
  `legend_title: str | None` field (figure-level, like
  `title`/`background_color`, since a legend belongs to the axes as a
  whole, not to any one mark), applied once in each backend's
  `apply_common_style`: matplotlib `ax.legend(title=...)`, re-issued
  only when a legend already exists (i.e. some mark set a `label` and
  its own renderer already called the label-less `ax.legend()`) to
  avoid a spurious "no artists with labels found" warning otherwise;
  bokeh `fig.legend.title = ...`, guarded the same way (`if
  fig.legend:`) since bokeh warns when setting a legend property with
  no legend yet added; altair re-`encode`s `color` with
  `alt.Legend(title=...)`, replacing the hardcoded
  `legend=alt.Legend(title=None)` `color_encoding` sets on a labeled
  mark -- Vega-Lite's shared top-level encoding on a `LayerSpec` makes
  this a no-op when no mark carries a label, same as every other
  backend; plotly `fig.update_layout(legend_title_text=...)`; xy
  appends an `xy.legend(title=...)` chrome child alongside the
  `x_axis`/`y_axis` pair `apply_common_style` already adds, needing no
  guard since an unlabeled `xy.legend()` simply draws nothing.
  `GridSpec`/`LayerSpec` themselves needed no change: `legend_title`
  is a `BaseSpec` field like `title`, so a `layer()` call already
  exposes it the same way `title` is exposed.
- **Marker shape.** Bokeh's `marker="square"` (vs. the implicit
  default circle) had no `ScatterSpec` equivalent: `ScatterSpec` had
  `color`, `size`, `edgecolor`, and `alpha`, but no shape field, so
  every plotmux scatter series rendered as whatever each backend's own
  default marker shape is, with no way to request a square, triangle,
  cross, etc. Closed by `ScatterSpec.marker: Literal["circle", "square",
  "triangle", "diamond", "cross", "x"] | None = None` (a small,
  backend-portable set rather than passing through each backend's full
  native marker vocabulary, mirroring how `LineSpec.linestyle` exposes
  four portable names rather than every backend's native dash
  vocabulary), translated per backend: matplotlib
  `Axes.scatter(marker=...)` via a `MARKER_STYLE` table
  (`plotmux.backends.matplotlib.scatter.MARKER_STYLE`, mapping to
  `"o"`/`"s"`/`"^"`/`"D"`/`"+"`/`"x"`); bokeh `figure.scatter(marker=
  ...)`, which accepts plotmux's own names directly, no table needed;
  altair `mark_point(shape=...)` via
  `plotmux.backends.altair.style.MARKER_STYLE` (`"circle"`/`"square"`/
  `"triangle-up"`/`"diamond"`/`"cross"` -- no `"x"` entry, altair's
  only asymmetry in this set, same pattern as `BarSpec.width`'s altair
  gap; `marker="x"` silently falls back to altair's own default shape
  rather than raising); plotly `go.Scatter(marker_symbol=...)` via
  `plotmux.backends.plotly.style.MARKER_STYLE` (every one of the six
  names has a direct plotly equivalent); xy `xy.scatter(symbol=...)`,
  which -- like bokeh -- accepts plotmux's own names directly.

Both gaps closed following the same precedent as the slope case study:
small, additive `BaseSpec`/`ScatterSpec` fields, no new mechanism.

## Case study: reproducing bokeh's log plot example

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
  `ymax=10.0**22`, `background_color="#fafafa"` -- all closed by the
  slope case study (see `BaseSpec.yscale`/`ymin`/`ymax`/
  `background_color`).
- **Labeled lines and line+scatter pairs sharing one legend entry,
  dashed/dotted line styles, per-line color and width.** Already
  `LineSpec.label`/`color`/`linewidth`/`linestyle` plus a `layer()`
  call per curve that needs both a line and a scatter on the same
  data, same as the legend case study's scatter+line merge -- no gap.

Three gaps were found, none raised by the slope or legend case
studies. All three are now closed:

- **Explicit x-axis bounds.** Bokeh's `x_range=(0, 5)` had no plotmux
  equivalent: `BaseSpec` had `ymin`/`ymax` (see the slope case study)
  but no `xmin`/`xmax` counterpart at the same figure level --
  `xmin`/`xmax` existed only on `HistogramSpec`/`CdfSpec`, resolved
  through `find_range`'s quantile-or-explicit convention against that
  spec's own single data array, which is a different feature (a
  data-driven bound) from a plain axis-range override that applies
  regardless of chart type. Closed by a `BaseSpec`-level
  `xmin: float | None`/`xmax: float | None` pair, explicit-value-only
  like `ymin`/`ymax` (not the quantile-string form), applied post-hoc
  in each backend's `apply_common_style` alongside `ymin`/`ymax`:
  matplotlib `Axes.set_xlim`; bokeh `figure.x_range.start`/`.end`;
  altair `alt.Scale(domainMin=..., domainMax=...)` on the x encoding;
  plotly `fig.update_layout(xaxis_range=[xmin, xmax])`, only forwarded
  when both bounds are set together (plotly's `xaxis.range` takes both
  at once, same "only both set together are forwarded" caveat
  `ymin`/`ymax` already documents for plotly/xy); xy
  `xy.x_axis(domain=(xmin, xmax))`, same both-bounds-together caveat.
  This sits alongside `HistogramSpec.xmin`/`CdfSpec.xmin` without
  replacing them -- those two remain quantile-capable and data-scoped
  (`float | str | None`, kept `kw_only=True` so redeclaring the field
  name in the subclass does not disturb `BaseSpec.values`'s
  required-field position in the generated `__init__`); the new field
  is a plain figure-level override open to every chart type, the
  `xmin`/`xmax` analogue of `ymin`/`ymax`. `BaseSpec._validate_base`'s
  `xmin > xmax` check guards with `isinstance(..., Real)` so it never
  fires on an unresolved quantile string from either subclass.
- **Legend position.** Bokeh's `p.legend.location = "top_left"` had no
  plotmux equivalent, the same shape of gap as the legend case study's
  once-open `legend_title` gap: `BaseSpec` had `legend_title` but
  nothing for legend *position*. Closed by a `BaseSpec`-level
  `legend_location: Literal["best", "top_left", "top_right",
  "bottom_left", "bottom_right", "top", "bottom", "left", "right"] |
  None = None` field, shipped alongside `legend_title` as one
  `legend_title`/`legend_location` pair rather than two unrelated
  additions, since both are set together in the bokeh original
  (`p.legend.title`/`p.legend.location`) and both apply post-hoc in the
  same `apply_common_style` step: matplotlib `ax.legend(loc=...)` via a
  `LEGEND_LOCATION` name-mapping table (matplotlib spells its own
  locations `"upper left"`-style; `"best"` already matches matplotlib's
  own name and needs no entry); bokeh `fig.legend.location = ...`,
  bokeh's own vocabulary directly except `"best"` (bokeh has no
  auto-placement location, so that one name is left as a no-op,
  falling back to bokeh's own default); altair
  `alt.Legend(orient=...)` via its own `LEGEND_LOCATION` table (altair's
  `orient` supports the four outer edges plus the four corners, all
  *outside* the plot area -- unlike matplotlib's inside-the-plot `loc`,
  so a given `legend_location` renders in a visibly different spot on
  altair, a small, permanent per-backend asymmetry; `"best"` again has
  no altair equivalent and is left as a no-op); plotly
  `fig.update_layout(legend=dict(x=..., y=..., xanchor=..., yanchor=
  ...))` via a name-to-fractional-coordinates table (plotly has no
  named corner enum, only `x`/`y`; `"best"` again a no-op); xy
  `xy.legend(loc=...)`, needing no translation table at all -- xy's own
  `legend_loc` validator underscore/space-tokenizes its input and
  matches plotmux's own portable names directly, `"best"` included (xy
  natively supports "best" auto-placement).
- **Hollow (no-fill) marker as a portable concept.** Distinct from the
  marker-*shape* gap in the legend case study: even with a circular
  marker, this example's `p.scatter(x, x**2, fill_color=None,
  line_color="olivedrab")` had no reliable plotmux equivalent because
  `ScatterSpec.color` has no "explicitly transparent" value distinct
  from "unset, use the backend default" -- `color=None` means the
  latter, and as the correction above notes, only bokeh's own default
  for an unset fill happens to be transparent; every other backend's
  default fill is opaque, so the same spec rendered filled markers on
  matplotlib/altair/plotly/xy and a hollow one only on bokeh. Closed by
  a tri-state `ScatterSpec.fill: bool | None = None` (`None`/`True` =
  filled, using `color`, unchanged behavior; `False` = no fill, drawing
  only the `edgecolor`/`color` outline), translated per backend:
  matplotlib `Axes.scatter(facecolors="none", edgecolors=<outline>)`
  when `fill is False` (`color` is popped from the call first --
  `Axes.scatter` rejects passing both `color` and `facecolors`/
  `edgecolors` at once); bokeh `fill_color=None` (today's accidental
  bokeh-only path becomes the explicit, intentional one); altair
  `mark_point(filled=False)`, overriding the `filled=True` the
  `edgecolor` path sets when both are given; plotly
  `go.Scatter(marker=dict(color="rgba(0, 0, 0, 0)"))` with the outline
  drawn via `marker.line` (already wired for `edgecolor`); xy
  `xy.scatter(color="rgba(0, 0, 0, 0)", stroke=<outline>,
  stroke_width=1.0)` -- xy has no dedicated "no fill" mark property
  either, so (like plotly) the fill is forced fully transparent and
  the outline carried by `stroke`.

All three closed following the same precedent as the slope and legend
case studies: small, additive `BaseSpec`/`ScatterSpec` fields, no new
mechanism. `legend_location` shipped together with the legend case
study's `legend_title` rather than separately, since both describe the
same `BaseSpec`-level "legend" concept and both are set together in
this example's own bokeh source.

## Case study: reproducing bokeh's stacked bar example

Checked against
[bokeh's `stacked` bar chart example](https://docs.bokeh.org/en/latest/docs/examples/basic/bars/stacked.html)
(one `vbar_stack` call stacking three year-series on top of each other
per fruit, a categorical (string) x-axis, a fixed 3-color palette, a
horizontal legend pinned top-left, hover tooltips, and assorted chrome
removal -- no gridlines, no minor ticks, no plot outline) to see
whether it is reproducible through plotmux's unified API, unchanged,
on all five backends. Unlike the slope/legend/log-plot case studies,
this was not close to reproducible: it needed one significant new
capability, hit a portability gap in an existing one, and legitimately
sits in the goal's stated non-goal territory for the rest.

- **Stacking.** No plotmux equivalent at all: `BarSpec` is a single
  series, and `layer()`'s `BarSpec` support draws each child's bars
  independently onto the shared axes with no coordination between
  them -- several `BarSpec`s at the same `x` positions simply overlap
  (each fully drawn, the last child on top), they do not stack into
  cumulative segments the way `vbar_stack` does. Closed by a new chart
  type, `StackedBarSpec(x, series: tuple[BarSeries, ...])` (a small
  per-series `(y, label, color)` tuple, mirroring how
  `LayerSpec.layers` holds a tuple of children) rather than overloading
  `layer()` -- stacking is a different composition rule from layering
  (cumulative y-offset vs. shared axes), so it earned its own spec and
  its own `_RENDERERS` entry per backend, the same reasoning that gave
  `BarSpec` itself its own spec rather than folding it into
  `HistogramSpec`: matplotlib `Axes.bar(..., bottom=running_total)`,
  incrementing `running_total` per series (matplotlib's own idiom for
  a stacked bar, no native stacking primitive); bokeh
  `figure.vbar_stack(names, x=..., source=...)` directly (bokeh's own
  primitive, matched almost one-to-one); altair
  `mark_bar().encode(x=..., y=..., color=...)` with the data reshaped
  long-form (one row per `(x, series)` pair) -- Vega-Lite stacks a bar
  mark automatically whenever `y` is quantitative and `color` is a
  discrete encoding, no explicit stacking argument needed; plotly
  `go.Bar` per series plus `fig.update_layout(barmode="stack")`; xy
  its own equivalent, checked against `xy.bar_chart`'s own API.
- **Categorical (string) x-axis.** `BarSpec.x` was typed and documented
  as an array of positions, and every renderer reflected that
  assumption inconsistently across backends when `x` actually held
  strings (e.g. `fruits = ["Apples", "Pears", ...]`, this example's
  own `x`): it worked, unchanged, on matplotlib and plotly (both
  accept a string `x` natively), but was broken on bokeh (needs a
  categorical `FactorRange` x_range constructed up front) and altair
  (hardcoded a quantitative `:Q` x encoding rather than a categorical
  `:N` one), and was unverified on xy. Closed by detecting a
  non-numeric `spec.x` and having bokeh's renderer construct its
  `figure` with a categorical `x_range` and altair's `render_bar`
  encode `x="x:N"` instead of `x="x:Q"` in that case, landed together
  with the stacking fix above since `StackedBarSpec`'s own `x` has
  exactly the same categorical-vs-numeric question.
- **Legend orientation** (`p.legend.orientation = "horizontal"`). A
  third legend-chrome field, alongside the legend case study's
  `legend_title` and the log-plot case study's `legend_location`, that
  plotmux had no equivalent for. Closed as a third field in the same
  batch: `legend_orientation: Literal["vertical", "horizontal"] | None
  = None`, applied in `apply_common_style`: matplotlib
  `ax.legend(ncols=len(handles))` when `"horizontal"` (matplotlib has
  no direct orientation flag, only a column count, so horizontal is
  approximated as one row); bokeh `fig.legend.orientation = ...`
  directly (bokeh's own vocabulary, matched one-to-one); altair
  `alt.Legend(direction=...)`; plotly
  `fig.update_layout(legend=dict(orientation="h" if ... else "v"))`;
  xy its own equivalent, checked against its legend API.

Deliberately **not** treated as gaps, matching the project goal's
stated non-goals:

- **Hover tooltips** (`tools="hover", tooltips="$name @fruits:
  @$name"`). An interactive, backend-specific power feature with no
  meaning on matplotlib (a static image) and no obvious common
  vocabulary across bokeh/plotly's very different tooltip-templating
  systems and altair's own `tooltip` encoding channel; reachable per
  backend via `Figure.to_native()`, the documented escape hatch for
  exactly this kind of niche, backend-specific feature, not a
  candidate for the unified API.
- **Gridline/minor-tick/outline removal, `toolbar_location=None`,
  `x_range.range_padding`.** Fine-grained chrome cosmetics with no
  existing common-style precedent (unlike `background_color`, which
  *is* on `BaseSpec` because every backend has an equally central
  notion of "figure background"); same escape-hatch treatment as
  above.

Stacking was the first of these four case studies to require a
genuinely new spec type rather than a new field on an existing one;
the categorical-x-axis fix was a prerequisite for stacking to be
usable with string categories (this example's own case) even though it
is independently useful for plain `BarSpec` too.
