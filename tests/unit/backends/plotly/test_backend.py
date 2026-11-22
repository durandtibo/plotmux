from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock

import numpy as np
import pytest

from plotmux.exceptions import UnsupportedSpecError
from plotmux.primitives import Bars, Line, Points
from plotmux.scene import AxesScene, GridScene, LegendStyle
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
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if TYPE_CHECKING:
    from pathlib import Path

if is_plotly_available():
    import plotly.graph_objects as go
    from plotly.graph_objects import Figure

    from plotmux.backends.plotly.backend import (
        PlotlyBackend,
        _add_axes,
        _legend_style,
        _trace,
        trace_bars,
        trace_line,
        trace_points,
    )


@pytest.fixture
def backend() -> PlotlyBackend:
    return PlotlyBackend()


def _panel(*marks: Any, **kwargs: Any) -> PanelSpec:
    return PanelSpec(marks=marks, **kwargs)


LINE = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
RED = (1.0, 0.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

#################################
#     Tests for PlotlyBackend   #
#################################


@plotly_available
def test_backend_name(backend: PlotlyBackend) -> None:
    assert backend.name == "plotly"


@plotly_available
def test_backend_capabilities_formats(backend: PlotlyBackend) -> None:
    assert backend.capabilities().formats == frozenset({"html", "json"})


@plotly_available
def test_backend_capabilities_grid_formats(backend: PlotlyBackend) -> None:
    assert backend.capabilities().grid_formats == frozenset({"html", "json"})


@plotly_available
def test_backend_capabilities_legend_locations(backend: PlotlyBackend) -> None:
    assert backend.capabilities().legend_locations == frozenset(
        {"top_left", "top_right", "bottom_left", "bottom_right", "top", "bottom", "left", "right"}
    )


@plotly_available
def test_backend_capabilities_markers(backend: PlotlyBackend) -> None:
    assert backend.capabilities().markers == frozenset(
        {"circle", "square", "triangle", "diamond", "cross", "x"}
    )


# --- render ---


@plotly_available
def test_backend_render_returns_a_figure(backend: PlotlyBackend) -> None:
    assert isinstance(backend.render(_panel(LINE)), Figure)


@plotly_available
def test_backend_render_histogram_has_one_bar_per_bin(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10)))
    assert len(fig.data[0].x) == 10


@plotly_available
def test_backend_render_histogram_density_integrates_to_one(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10, density=True)))
    assert float((fig.data[0].y * fig.data[0].width).sum()) == pytest.approx(1.0)


@plotly_available
def test_backend_render_cdf_goes_from_zero_to_one(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(CdfSpec(values=np.arange(11.0))))
    y = fig.data[0].y
    assert (y[0], y[-1]) == (0.0, 1.0)


@plotly_available
def test_backend_render_stacked_bar_in_a_layer(backend: PlotlyBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3), series=(BarSeries(y=np.arange(3)), BarSeries(y=np.arange(3)))
    )
    assert len(backend.render(_panel(stacked, LINE)).data) == 3


@plotly_available
def test_backend_render_stacked_bar_uses_the_base(backend: PlotlyBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.array([1, 2, 3])), BarSeries(y=np.array([4, 5, 6]))),
    )
    assert backend.render(_panel(stacked)).data[1].base.tolist() == [1.0, 2.0, 3.0]


@plotly_available
def test_backend_render_bars_overlay(backend: PlotlyBackend) -> None:
    assert (
        backend.render(_panel(BarSpec(x=np.arange(3), y=np.arange(3)))).layout.barmode == "overlay"
    )


@plotly_available
def test_backend_render_layer_draws_every_mark(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(LINE, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert [t.mode for t in fig.data] == ["lines", "markers"]


@plotly_available
def test_backend_render_slope_alone(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1))
    assert list(fig.data[0].y) == [0.0, 2.0]


@plotly_available
def test_backend_render_slope_in_a_grid(backend: PlotlyBackend) -> None:
    grid = GridSpec(panels=(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1),))
    assert len(backend.render(grid).data) == 1


@plotly_available
def test_backend_render_categorical_x_order(backend: PlotlyBackend) -> None:
    fig = backend.render(_panel(BarSpec(x=np.array(["b", "a"]), y=np.arange(2))))
    assert fig.layout.xaxis.categoryarray == ("b", "a")


@plotly_available
def test_backend_render_numeric_x_has_no_category_order(backend: PlotlyBackend) -> None:
    assert backend.render(_panel(LINE)).layout.xaxis.categoryarray is None


@plotly_available
def test_backend_render_title(backend: PlotlyBackend) -> None:
    assert backend.render(_panel(LINE, title="t")).layout.title.text == "t"


@plotly_available
def test_backend_render_legend_style(backend: PlotlyBackend) -> None:
    mark = LineSpec(x=np.arange(3), y=np.arange(3), label="a")
    fig = backend.render(_panel(mark, legend_title="l", legend_location="top"))
    assert (fig.layout.legend.title.text, fig.layout.legend.xanchor) == ("l", "center")


@plotly_available
def test_backend_render_grid_one_trace_per_mark(backend: PlotlyBackend) -> None:
    assert len(backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2)).data) == 3


@plotly_available
def test_backend_render_grid_subplot_axes(backend: PlotlyBackend) -> None:
    fig = backend.render(GridSpec(panels=(_panel(LINE),) * 2, ncols=2))
    assert [t.xaxis for t in fig.data] == ["x", "x2"]


@plotly_available
def test_backend_render_grid_subplot_titles(backend: PlotlyBackend) -> None:
    fig = backend.render(GridSpec(panels=(_panel(LINE, title="a <b>"), _panel(LINE))))
    assert [a.text for a in fig.layout.annotations] == ["a &lt;b&gt;"]


@plotly_available
def test_backend_render_grid_title(backend: PlotlyBackend) -> None:
    assert backend.render(GridSpec(panels=(_panel(LINE),), title="t")).layout.title.text == "t"


@plotly_available
def test_backend_render_grid_styles_each_panel(backend: PlotlyBackend) -> None:
    fig = backend.render(
        GridSpec(panels=(_panel(LINE, xlabel="a"), _panel(LINE, xlabel="b")), ncols=2)
    )
    assert (fig.layout.xaxis.title.text, fig.layout.xaxis2.title.text) == ("a", "b")


@plotly_available
def test_backend_render_grid_background_is_per_panel(backend: PlotlyBackend) -> None:
    grid = GridSpec(panels=(_panel(LINE, background_color="red"), _panel(LINE)), ncols=2)
    assert [s.xref for s in backend.render(grid).layout.shapes] == ["x domain"]


@plotly_available
def test_backend_render_grid_legend_is_the_first_panels(backend: PlotlyBackend) -> None:
    labeled = LineSpec(x=np.arange(3), y=np.arange(3), label="a")
    grid = GridSpec(panels=(_panel(LINE), _panel(labeled, legend_title="l")), ncols=2)
    assert backend.render(grid).layout.legend.title.text == "l"


@plotly_available
def test_backend_render_every_marker_is_supported(backend: PlotlyBackend) -> None:
    mark = ScatterSpec(x=np.arange(3), y=np.arange(3), marker="x")
    assert backend.render(_panel(mark)).data[0].marker.symbol == "x"


@plotly_available
def test_backend_render_unsupported_legend_location_raises(backend: PlotlyBackend) -> None:
    scene = AxesScene(primitives=(), legend=LegendStyle(location=cast("Any", "best")))
    with pytest.raises(UnsupportedSpecError, match="does not support legend_location='best'"):
        backend.capabilities().check(scene)


@plotly_available
def test_backend_render_does_not_change_the_spec(backend: PlotlyBackend) -> None:
    spec = _panel(LINE)
    backend.render(spec)
    assert spec == _panel(LINE)


@plotly_available
def test_backend_draw_axes_scene(backend: PlotlyBackend) -> None:
    assert isinstance(backend.draw(AxesScene(primitives=())), Figure)


@plotly_available
def test_backend_draw_grid_scene(backend: PlotlyBackend) -> None:
    scene = GridScene(panels=(AxesScene(primitives=()),) * 2, ncols=2)
    assert isinstance(backend.draw(scene), Figure)


# --- save ---


@pytest.mark.parametrize("fmt", ["html", "json"])
@plotly_available
def test_backend_save_supported_formats(backend: PlotlyBackend, tmp_path: Path, fmt: str) -> None:
    path = tmp_path / f"fig.{fmt}"
    backend.save(backend.render(_panel(LINE)), path, fmt)
    assert path.stat().st_size > 0


@plotly_available
def test_backend_save_json_is_json(backend: PlotlyBackend, tmp_path: Path) -> None:
    path = tmp_path / "fig.json"
    backend.save(backend.render(_panel(LINE)), path, "json")
    assert path.read_text(encoding="utf-8").startswith("{")


@plotly_available
def test_backend_save_grid(backend: PlotlyBackend, tmp_path: Path) -> None:
    path = tmp_path / "grid.html"
    backend.save(backend.render(GridSpec(panels=(_panel(LINE),))), path, "html")
    assert path.stat().st_size > 0


@plotly_available
def test_backend_show_calls_figure_show(backend: PlotlyBackend) -> None:
    native = Mock()
    backend.show(native)
    native.show.assert_called_once_with()


###############################
#     Tests for trace_bars    #
###############################


def _bars(**kwargs: Any) -> Bars:
    defaults: dict[str, Any] = {
        "x": np.array([1.0, 3.0]),
        "height": np.array([2.0, 4.0]),
        "base": np.array([0.0, 1.0]),
        "width": np.array([2.0, 1.0]),
        "color": RED,
    }
    return Bars(**{**defaults, **kwargs})


@plotly_available
def test_trace_bars_data() -> None:
    trace = trace_bars(_bars())
    assert (trace.x.tolist(), trace.y.tolist(), trace.base.tolist()) == (
        [1.0, 3.0],
        [2.0, 4.0],
        [0.0, 1.0],
    )


@plotly_available
def test_trace_bars_array_width() -> None:
    assert trace_bars(_bars()).width.tolist() == [2.0, 1.0]


@plotly_available
def test_trace_bars_scalar_width() -> None:
    assert trace_bars(_bars(width=0.5)).width == 0.5


@plotly_available
def test_trace_bars_color() -> None:
    assert trace_bars(_bars()).marker.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_bars_without_color() -> None:
    assert trace_bars(_bars(color=None)).marker.color is None


@plotly_available
def test_trace_bars_alpha() -> None:
    assert trace_bars(_bars(alpha=0.5)).opacity == 0.5


@plotly_available
def test_trace_bars_label() -> None:
    trace = trace_bars(_bars(label="a"))
    assert (trace.name, trace.showlegend) == ("a", True)


@plotly_available
def test_trace_bars_categorical() -> None:
    assert trace_bars(_bars(x=np.array(["a", "b"]))).x.tolist() == ["a", "b"]


###############################
#     Tests for trace_line    #
###############################


def _line(**kwargs: Any) -> Line:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Line(**{**defaults, **kwargs})


@plotly_available
def test_trace_line_data() -> None:
    trace = trace_line(_line())
    assert (trace.mode, trace.x.tolist(), trace.y.tolist()) == ("lines", [0.0, 1.0], [2.0, 3.0])


@plotly_available
def test_trace_line_style() -> None:
    trace = trace_line(_line(alpha=0.5, linewidth=3.0, linestyle="dashed"))
    assert (trace.opacity, trace.line.width, trace.line.dash) == (0.5, 3.0, "dash")


@plotly_available
def test_trace_line_color() -> None:
    assert trace_line(_line()).line.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_line_solid_dash() -> None:
    assert trace_line(_line()).line.dash == "solid"


@plotly_available
def test_trace_line_label() -> None:
    trace = trace_line(_line(label="a"))
    assert (trace.name, trace.showlegend) == ("a", True)


@plotly_available
def test_trace_line_infinite_is_the_segment() -> None:
    assert trace_line(_line(infinite=(2.0, 1.0))).x.tolist() == [0.0, 1.0]


@plotly_available
def test_trace_line_nan_is_kept() -> None:
    assert np.isnan(trace_line(_line(y=np.array([1.0, np.nan]))).y[1])


@plotly_available
def test_trace_line_without_color() -> None:
    assert trace_line(_line(color=None)).line.color is None


#################################
#     Tests for trace_points    #
#################################


def _points(**kwargs: Any) -> Points:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Points(**{**defaults, **kwargs})


@plotly_available
def test_trace_points_data() -> None:
    trace = trace_points(_points())
    assert (trace.mode, trace.x.tolist(), trace.y.tolist()) == ("markers", [0.0, 1.0], [2.0, 3.0])


@plotly_available
def test_trace_points_color() -> None:
    assert trace_points(_points()).marker.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_points_size() -> None:
    assert trace_points(_points(size=7.0)).marker.size == 7.0


@plotly_available
def test_trace_points_alpha() -> None:
    assert trace_points(_points(alpha=0.5)).opacity == 0.5


@plotly_available
def test_trace_points_marker() -> None:
    assert trace_points(_points(marker="triangle")).marker.symbol == "triangle-up"


@plotly_available
def test_trace_points_edgecolor() -> None:
    assert trace_points(_points(edgecolor=BLUE)).marker.line.color == "rgba(0, 0, 255, 1.0)"


@plotly_available
def test_trace_points_edge_defaults_to_the_color() -> None:
    assert trace_points(_points()).marker.line.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_points_hollow_is_transparent() -> None:
    assert trace_points(_points(fill=False)).marker.color == "rgba(0, 0, 0, 0)"


@plotly_available
def test_trace_points_hollow_outline_is_the_color() -> None:
    assert trace_points(_points(fill=False)).marker.line.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_points_hollow_outline_is_the_edgecolor() -> None:
    trace = trace_points(_points(fill=False, edgecolor=BLUE))
    assert trace.marker.line.color == "rgba(0, 0, 255, 1.0)"


@plotly_available
def test_trace_points_fill_true_is_filled() -> None:
    assert trace_points(_points(fill=True)).marker.color == "rgba(255, 0, 0, 1.0)"


@plotly_available
def test_trace_points_label() -> None:
    trace = trace_points(_points(label="a"))
    assert (trace.name, trace.showlegend) == ("a", True)


###########################################
#     Tests for _trace/_legend_style/etc  #
###########################################


@plotly_available
def test_trace_bars() -> None:
    assert isinstance(_trace(_bars()), go.Bar)


@plotly_available
def test_trace_line() -> None:
    assert cast("Any", _trace(_line())).mode == "lines"


@plotly_available
def test_trace_points() -> None:
    assert cast("Any", _trace(_points())).mode == "markers"


@pytest.mark.parametrize(
    ("label", "alpha", "expected"),
    [
        (None, None, {}),
        ("a", None, {"name": "a", "showlegend": True}),
        (None, 0.5, {"opacity": 0.5}),
        ("a", 0.5, {"name": "a", "showlegend": True, "opacity": 0.5}),
    ],
)
@plotly_available
def test_legend_style(label: str | None, alpha: float | None, expected: dict[str, Any]) -> None:
    assert _legend_style(label, alpha) == expected


@plotly_available
def test_add_axes_adds_the_traces_in_order() -> None:
    fig = go.Figure()
    _add_axes(fig, AxesScene(primitives=(_line(), _points())))
    assert [t.mode for t in fig.data] == ["lines", "markers"]


@plotly_available
def test_add_axes_applies_the_style() -> None:
    fig = go.Figure()
    _add_axes(fig, AxesScene(primitives=(), xlabel="x"))
    assert fig.layout.xaxis.title.text == "x"


@plotly_available
def test_add_axes_categories() -> None:
    fig = go.Figure()
    _add_axes(fig, AxesScene(primitives=(), categories=("b", "a")))
    assert fig.layout.xaxis.categoryarray == ("b", "a")


@plotly_available
def test_trace_points_without_color_has_no_marker_color() -> None:
    assert trace_points(_points(color=None)).marker.color is None


@plotly_available
def test_trace_points_without_color_and_with_size() -> None:
    assert trace_points(_points(color=None, size=3.0)).marker.size == 3.0
