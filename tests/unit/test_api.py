from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
import pytest

import plotmux
from plotmux.api import _as_panel, _merge_axes_options
from plotmux.backends.registry import _REGISTRY, register_backend
from plotmux.exceptions import InvalidSpecError
from plotmux.scene import build_scene
from plotmux.specs import (
    BarSeries,
    BarSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)
from tests.fakes import FakeBackend

if TYPE_CHECKING:
    from collections.abc import Iterator

    from plotmux.figure import Figure


@pytest.fixture(autouse=True)
def _fake_backend() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    register_backend(FakeBackend())
    with plotmux.backend("fake"):
        yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def _panel(figure: Figure) -> PanelSpec:
    return cast("PanelSpec", figure.spec)


def _mark(figure: Figure) -> Any:
    return _panel(figure).marks[0]


##########################
#     Tests for hist     #
##########################


def test_hist_builds_a_panel_with_a_histogram() -> None:
    assert _panel(plotmux.hist(np.arange(101), bins=10, backend="fake")) == PanelSpec(
        marks=(HistogramSpec(values=np.arange(101), bins=10),)
    )


def test_hist_returns_a_figure_of_the_backend() -> None:
    assert plotmux.hist(np.arange(11), backend="fake").backend_name == "fake"


def test_hist_native_is_the_render_of_the_backend() -> None:
    fig = plotmux.hist(np.arange(11), backend="fake")
    assert fig.native == build_scene(fig.spec)


def test_hist_uses_the_default_backend() -> None:
    assert plotmux.hist(np.arange(11)).backend_name == "fake"


def test_hist_default_mark() -> None:
    mark = _mark(plotmux.hist(np.arange(101), backend="fake"))
    assert (mark.bins, mark.density, mark.color, mark.xmin, mark.xmax) == (
        30,
        False,
        None,
        None,
        None,
    )


def test_hist_mark_options() -> None:
    mark = _mark(
        plotmux.hist(
            [1, 2, 3],
            bins=3,
            xmin="q0.1",
            xmax=3,
            density=True,
            label="a",
            color="red",
            alpha=0.5,
            backend="fake",
        )
    )
    assert (mark.bins, mark.xmin, mark.xmax, mark.density, mark.label, mark.alpha) == (
        3,
        "q0.1",
        3,
        True,
        "a",
        0.5,
    )


def test_hist_xmin_is_the_range_of_the_data_and_not_an_axis_limit() -> None:
    assert _panel(plotmux.hist(np.arange(11), xmin=2, xmax=4, backend="fake")).xmin is None


def test_hist_panel_options() -> None:
    panel = _panel(
        plotmux.hist(
            np.arange(11),
            title="t",
            xlabel="x",
            ylabel="y",
            xscale="log",
            yscale="log",
            ymin=1,
            ymax=2,
            background_color="#ff0000",
            legend_title="l",
            legend_location="top",
            legend_orientation="horizontal",
            backend="fake",
        )
    )
    assert panel == PanelSpec(
        marks=(HistogramSpec(values=np.arange(11)),),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
        ymin=1,
        ymax=2,
        background_color="#ff0000",
        legend_title="l",
        legend_location="top",
        legend_orientation="horizontal",
    )


def test_hist_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.hist(np.arange(11), backend="does-not-exist")


def test_hist_invalid_bins_raises() -> None:
    with pytest.raises(InvalidSpecError, match="bins must be a positive integer"):
        plotmux.hist(np.arange(11), bins=0, backend="fake")


def test_hist_ymin_greater_than_ymax_raises() -> None:
    with pytest.raises(InvalidSpecError, match="ymin must not be greater than ymax"):
        plotmux.hist(np.arange(11), ymin=10, ymax=0, backend="fake")


def test_hist_misspelled_keyword_raises() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'colour'"):
        cast("Any", plotmux.hist)(np.arange(11), colour="red", backend="fake")


def test_hist_has_no_keyword_pass_through() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'bandwidth'"):
        cast("Any", plotmux.hist)(np.arange(11), bandwidth=1, backend="fake")


#########################
#     Tests for cdf     #
#########################


def test_cdf_builds_a_panel_with_a_cdf() -> None:
    assert _panel(plotmux.cdf([1, 2, 3], nbins=2, backend="fake")) == PanelSpec(
        marks=(CdfSpec(values=np.array([1, 2, 3]), nbins=2),), ylabel="cumulative probability"
    )


def test_cdf_ylabel_can_be_overridden() -> None:
    assert _panel(plotmux.cdf([1, 2, 3], ylabel="p", backend="fake")).ylabel == "p"


def test_cdf_ylabel_can_be_removed() -> None:
    assert _panel(plotmux.cdf([1, 2, 3], ylabel=None, backend="fake")).ylabel is None


def test_cdf_mark_options() -> None:
    mark = _mark(
        plotmux.cdf(
            [1, 2, 3], xmin=1, xmax="q0.9", label="a", color="red", alpha=0.5, backend="fake"
        )
    )
    assert (mark.xmin, mark.xmax, mark.label, mark.alpha) == (1, "q0.9", "a", 0.5)


def test_cdf_invalid_nbins_raises() -> None:
    with pytest.raises(InvalidSpecError, match="nbins must be a positive integer"):
        plotmux.cdf([1, 2, 3], nbins=0, backend="fake")


def test_cdf_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.cdf([1, 2, 3], backend="does-not-exist")


#########################
#     Tests for line    #
#########################


def test_line_builds_a_panel_with_a_line() -> None:
    assert _panel(plotmux.line([1, 2], [3, 4], backend="fake")) == PanelSpec(
        marks=(LineSpec(x=np.array([1, 2]), y=np.array([3, 4])),)
    )


def test_line_mark_options() -> None:
    mark = _mark(
        plotmux.line(
            [1, 2],
            [3, 4],
            label="a",
            color="red",
            alpha=0.5,
            linewidth=2,
            linestyle="dashed",
            backend="fake",
        )
    )
    assert (mark.label, mark.alpha, mark.linewidth, mark.linestyle) == ("a", 0.5, 2, "dashed")


def test_line_axis_limits() -> None:
    panel = _panel(plotmux.line([1, 2], [3, 4], xmin=0, xmax=5, backend="fake"))
    assert (panel.xmin, panel.xmax) == (0, 5)


def test_line_mismatched_length_raises() -> None:
    with pytest.raises(InvalidSpecError, match="x and y must have the same length"):
        plotmux.line([1, 2], [3], backend="fake")


def test_line_invalid_color_raises() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        plotmux.line([1, 2], [3, 4], color="not-a-color", backend="fake")


def test_line_xmin_greater_than_xmax_raises() -> None:
    with pytest.raises(InvalidSpecError, match="xmin must not be greater than xmax"):
        plotmux.line([1, 2], [3, 4], xmin=5, xmax=0, backend="fake")


############################
#     Tests for scatter    #
############################


def test_scatter_builds_a_panel_with_a_scatter() -> None:
    assert _panel(plotmux.scatter([1, 2], [3, 4], backend="fake")) == PanelSpec(
        marks=(ScatterSpec(x=np.array([1, 2]), y=np.array([3, 4])),)
    )


def test_scatter_mark_options() -> None:
    mark = _mark(
        plotmux.scatter(
            [1, 2],
            [3, 4],
            label="a",
            color="red",
            size=3,
            edgecolor="blue",
            alpha=0.5,
            marker="circle",
            fill=False,
            backend="fake",
        )
    )
    assert (mark.label, mark.size, mark.alpha, mark.marker, mark.fill) == (
        "a",
        3,
        0.5,
        "circle",
        False,
    )


def test_scatter_invalid_size_raises() -> None:
    with pytest.raises(InvalidSpecError, match="size must be a positive number"):
        plotmux.scatter([1, 2], [3, 4], size=0, backend="fake")


###########################
#     Tests for bar       #
###########################


def test_bar_builds_a_panel_with_a_bar() -> None:
    assert _panel(plotmux.bar(["a", "b"], [1, 2], width=0.5, backend="fake")) == PanelSpec(
        marks=(BarSpec(x=np.array(["a", "b"]), y=np.array([1, 2]), width=0.5),)
    )


def test_bar_mark_options() -> None:
    mark = _mark(plotmux.bar([1, 2], [3, 4], label="a", color="red", alpha=0.5, backend="fake"))
    assert (mark.label, mark.alpha) == ("a", 0.5)


def test_bar_invalid_width_raises() -> None:
    with pytest.raises(InvalidSpecError, match="width must be a positive number"):
        plotmux.bar([1, 2], [3, 4], width=0, backend="fake")


###################################
#     Tests for stacked_bar       #
###################################


def test_stacked_bar_builds_a_panel_with_a_stacked_bar() -> None:
    series = (BarSeries(y=np.array([1, 2]), label="a"),)
    assert _panel(plotmux.stacked_bar(["x", "y"], series, alpha=0.5, backend="fake")) == PanelSpec(
        marks=(StackedBarSpec(x=np.array(["x", "y"]), series=series, alpha=0.5),)
    )


def test_stacked_bar_empty_series_raises() -> None:
    with pytest.raises(InvalidSpecError, match="series must contain at least one BarSeries"):
        plotmux.stacked_bar(["x", "y"], [], backend="fake")


##########################
#     Tests for slope    #
##########################


def test_slope_builds_a_panel_with_a_slope() -> None:
    assert _panel(plotmux.slope(2, 10, xmin=0, xmax=5, backend="fake")) == PanelSpec(
        marks=(SlopeSpec(gradient=2, intercept=10),), xmin=0, xmax=5
    )


def test_slope_mark_options() -> None:
    mark = _mark(
        plotmux.slope(
            2,
            label="a",
            color="red",
            linewidth=3,
            linestyle="dotted",
            alpha=0.5,
            xmin=0,
            xmax=1,
            backend="fake",
        )
    )
    assert (mark.label, mark.linewidth, mark.linestyle, mark.alpha) == ("a", 3, "dotted", 0.5)


def test_slope_without_extent_raises() -> None:
    with pytest.raises(InvalidSpecError, match="needs the x extent of the panel"):
        plotmux.slope(2, 10, backend="fake")


###########################
#     Tests for layer     #
###########################


def test_layer_of_marks() -> None:
    hist = HistogramSpec(values=np.arange(11))
    line = LineSpec(x=np.arange(3), y=np.arange(3))
    assert _panel(plotmux.layer(hist, line, backend="fake")) == PanelSpec(marks=(hist, line))


def test_layer_of_figures_takes_their_marks() -> None:
    fig = plotmux.layer(plotmux.hist(np.arange(11)), plotmux.line([1, 2], [3, 4]), backend="fake")
    assert [type(m).__name__ for m in _panel(fig).marks] == ["HistogramSpec", "LineSpec"]


def test_layer_of_a_layer_flattens() -> None:
    inner = plotmux.layer(
        plotmux.line([1, 2], [3, 4]), plotmux.line([1, 2], [5, 6]), backend="fake"
    )
    outer = plotmux.layer(inner, plotmux.line([1, 2], [7, 8]), backend="fake")
    assert len(_panel(outer).marks) == 3


def test_layer_single_item() -> None:
    assert len(_panel(plotmux.layer(plotmux.line([1, 2], [3, 4]), backend="fake")).marks) == 1


def test_layer_slope_uses_the_data_of_a_sibling() -> None:
    fig = plotmux.layer(plotmux.line([1, 5], [3, 4]), SlopeSpec(gradient=1.0), backend="fake")
    assert len(_panel(fig).marks) == 2


def test_layer_slope_alone_raises() -> None:
    with pytest.raises(InvalidSpecError, match="needs the x extent of the panel"):
        plotmux.layer(SlopeSpec(gradient=1.0), backend="fake")


def test_layer_figure_title_is_kept() -> None:
    fig = plotmux.layer(
        plotmux.line([1, 2], [3, 4], title="t"), plotmux.line([1, 2], [5, 6]), backend="fake"
    )
    assert _panel(fig).title == "t"


def test_layer_call_option_wins_over_the_figures() -> None:
    fig = plotmux.layer(plotmux.line([1, 2], [3, 4], title="t"), title="call", backend="fake")
    assert _panel(fig).title == "call"


def test_layer_same_option_on_two_figures_is_not_a_conflict() -> None:
    fig = plotmux.layer(
        plotmux.line([1, 2], [3, 4], title="t"),
        plotmux.line([1, 2], [5, 6], title="t"),
        backend="fake",
    )
    assert _panel(fig).title == "t"


def test_layer_conflicting_options_raise() -> None:
    with pytest.raises(
        InvalidSpecError, match=r"the figures have different values of title: \['a', 'b'\]"
    ):
        plotmux.layer(
            plotmux.line([1, 2], [3, 4], title="a"),
            plotmux.line([1, 2], [5, 6], title="b"),
            backend="fake",
        )


def test_layer_conflict_is_resolved_by_the_call() -> None:
    fig = plotmux.layer(
        plotmux.line([1, 2], [3, 4], title="a"),
        plotmux.line([1, 2], [5, 6], title="b"),
        title="c",
        backend="fake",
    )
    assert _panel(fig).title == "c"


def test_layer_empty_raises() -> None:
    with pytest.raises(InvalidSpecError, match="marks must contain at least one mark"):
        plotmux.layer(backend="fake")


def test_layer_grid_item_raises() -> None:
    inner = plotmux.grid(plotmux.line([1, 2], [3, 4]), backend="fake")
    with pytest.raises(InvalidSpecError, match="a grid cannot be an item of layer or grid"):
        plotmux.layer(inner, backend="fake")


def test_layer_ymin_greater_than_ymax_raises() -> None:
    with pytest.raises(InvalidSpecError, match="ymin must not be greater than ymax"):
        plotmux.layer(plotmux.line([1, 2], [3, 4]), ymin=10, ymax=0, backend="fake")


def test_layer_invalid_background_color_raises() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        plotmux.layer(plotmux.line([1, 2], [3, 4]), background_color="not-a-color", backend="fake")


def test_layer_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.layer(plotmux.line([1, 2], [3, 4]), backend="does-not-exist")


def test_layer_does_not_change_the_figures() -> None:
    first = plotmux.line([1, 2], [3, 4], title="t")
    plotmux.layer(first, title="other", backend="fake")
    assert _panel(first).title == "t"


##########################
#     Tests for grid     #
##########################


def test_grid_of_marks_wraps_each_in_a_panel() -> None:
    hist = HistogramSpec(values=np.arange(11))
    line = LineSpec(x=np.arange(3), y=np.arange(3))
    assert plotmux.grid(hist, line, ncols=2, title="t", backend="fake").spec == GridSpec(
        panels=(PanelSpec(marks=(hist,)), PanelSpec(marks=(line,))), ncols=2, title="t"
    )


def test_grid_of_figures_keeps_their_panels() -> None:
    first = plotmux.line([1, 2], [3, 4], title="a")
    grid = plotmux.grid(first, backend="fake").spec
    assert cast("GridSpec", grid).panels == (first.spec,)


def test_grid_of_a_layer_figure() -> None:
    layer = plotmux.layer(plotmux.line([1, 2], [3, 4]), SlopeSpec(gradient=1.0), backend="fake")
    assert len(cast("GridSpec", plotmux.grid(layer, backend="fake").spec).panels[0].marks) == 2


def test_grid_default_ncols_is_one() -> None:
    assert (
        cast("GridSpec", plotmux.grid(plotmux.line([1, 2], [3, 4]), backend="fake").spec).ncols == 1
    )


def test_grid_returns_a_figure_of_the_backend() -> None:
    assert plotmux.grid(plotmux.line([1, 2], [3, 4]), backend="fake").backend_name == "fake"


def test_grid_empty_raises() -> None:
    with pytest.raises(InvalidSpecError, match="panels must contain at least one panel"):
        plotmux.grid(backend="fake")


def test_grid_nested_grid_item_raises() -> None:
    inner = plotmux.grid(plotmux.line([1, 2], [3, 4]), backend="fake")
    with pytest.raises(InvalidSpecError, match="a grid cannot be an item of layer or grid"):
        plotmux.grid(inner, backend="fake")


def test_grid_invalid_ncols_raises() -> None:
    with pytest.raises(InvalidSpecError, match="ncols must be a positive integer"):
        plotmux.grid(plotmux.line([1, 2], [3, 4]), ncols=0, backend="fake")


def test_grid_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.grid(plotmux.line([1, 2], [3, 4]), backend="does-not-exist")


def test_grid_has_no_axes_options() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'xlabel'"):
        cast("Any", plotmux.grid)(plotmux.line([1, 2], [3, 4]), xlabel="x", backend="fake")


############################
#     Tests for _as_panel  #
############################


def test_as_panel_of_a_mark() -> None:
    line = LineSpec(x=np.arange(3), y=np.arange(3))
    assert _as_panel(line) == PanelSpec(marks=(line,))


def test_as_panel_of_a_panel() -> None:
    panel = PanelSpec(marks=(LineSpec(x=np.arange(3), y=np.arange(3)),), title="t")
    assert _as_panel(panel) is panel


def test_as_panel_of_a_figure() -> None:
    fig = plotmux.line([1, 2], [3, 4], backend="fake")
    assert _as_panel(fig) is fig.spec


def test_as_panel_of_a_grid_raises() -> None:
    grid = GridSpec(panels=(PanelSpec(marks=(LineSpec(x=np.arange(3), y=np.arange(3)),)),))
    with pytest.raises(InvalidSpecError, match="a grid cannot be an item"):
        _as_panel(cast("Any", grid))


#####################################
#     Tests for _merge_axes_options #
#####################################

LINE = LineSpec(x=np.arange(3), y=np.arange(3))


def test_merge_axes_options_no_panel_returns_the_explicit_options() -> None:
    assert _merge_axes_options([], {"title": "t", "backend": "fake"}) == {
        "title": "t",
        "backend": "fake",
    }


def test_merge_axes_options_default_values_are_not_merged() -> None:
    assert _merge_axes_options([PanelSpec(marks=(LINE,))], {}) == {}


def test_merge_axes_options_takes_the_non_default_value() -> None:
    panels = [PanelSpec(marks=(LINE,), xlabel="x"), PanelSpec(marks=(LINE,))]
    assert _merge_axes_options(panels, {}) == {"xlabel": "x"}


def test_merge_axes_options_merges_several_fields() -> None:
    panels = [
        PanelSpec(marks=(LINE,), xlabel="x"),
        PanelSpec(marks=(LINE,), ylabel="y", yscale="log"),
    ]
    assert _merge_axes_options(panels, {}) == {"xlabel": "x", "ylabel": "y", "yscale": "log"}


def test_merge_axes_options_explicit_wins_over_a_conflict() -> None:
    panels = [PanelSpec(marks=(LINE,), xlabel="a"), PanelSpec(marks=(LINE,), xlabel="b")]
    assert _merge_axes_options(panels, {"xlabel": "c"}) == {"xlabel": "c"}


def test_merge_axes_options_conflict_raises() -> None:
    panels = [PanelSpec(marks=(LINE,), ymax=1), PanelSpec(marks=(LINE,), ymax=2)]
    with pytest.raises(InvalidSpecError, match=r"different values of ymax: \[1, 2\]"):
        _merge_axes_options(panels, {})


def test_merge_axes_options_does_not_merge_the_marks() -> None:
    assert "marks" not in _merge_axes_options([PanelSpec(marks=(LINE,), title="t")], {})
