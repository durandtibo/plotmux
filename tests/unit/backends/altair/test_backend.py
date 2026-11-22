from __future__ import annotations

import csv
import io
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
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if TYPE_CHECKING:
    from pathlib import Path

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.backend import (
        AltairBackend,
        _chart,
        _draw_axes,
        _empty_chart,
        _mark_chart,
        chart_bars,
        chart_line,
        chart_points,
    )


@pytest.fixture
def backend() -> AltairBackend:
    return AltairBackend()


def _panel(*marks: Any, **kwargs: Any) -> PanelSpec:
    return PanelSpec(marks=marks, **kwargs)


def _layers(chart: Any) -> list[dict[str, Any]]:
    r"""Return the layers of a chart as dicts, with the rows of their data."""
    spec = chart.to_dict()
    layers = spec.get("layer", [spec])
    result = []
    for layer in layers:
        text = spec["datasets"][layer["data"]["name"]]
        rows = list(csv.DictReader(io.StringIO(text)))
        result.append({**layer, "rows": rows})
    return result


def _column(layer: dict[str, Any], name: str) -> list[str]:
    return [row[name] for row in layer["rows"]]


LINE = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
RED = (1.0, 0.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

#################################
#     Tests for AltairBackend   #
#################################


@altair_available
def test_backend_name(backend: AltairBackend) -> None:
    assert backend.name == "altair"


@altair_available
def test_backend_capabilities_formats(backend: AltairBackend) -> None:
    assert backend.capabilities().formats == frozenset({"html", "json"})


@altair_available
def test_backend_capabilities_grid_formats(backend: AltairBackend) -> None:
    assert backend.capabilities().grid_formats == frozenset({"html", "json"})


@altair_available
def test_backend_capabilities_legend_locations(backend: AltairBackend) -> None:
    assert backend.capabilities().legend_locations == frozenset(
        {"top_left", "top_right", "bottom_left", "bottom_right", "top", "bottom", "left", "right"}
    )


@altair_available
def test_backend_capabilities_markers(backend: AltairBackend) -> None:
    assert backend.capabilities().markers == frozenset(
        {"circle", "square", "triangle", "diamond", "cross", "x"}
    )


# --- render ---


@altair_available
def test_backend_render_returns_a_chart(backend: AltairBackend) -> None:
    assert isinstance(backend.render(_panel(LINE)), alt.Chart)


@altair_available
def test_backend_render_histogram_has_one_bar_per_bin(backend: AltairBackend) -> None:
    chart = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10)))
    assert len(_layers(chart)[0]["rows"]) == 10


@altair_available
def test_backend_render_histogram_density_integrates_to_one(backend: AltairBackend) -> None:
    chart = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10, density=True)))
    (layer,) = _layers(chart)
    area = sum(
        (float(r["y"]) - float(r["y2"])) * (float(r["x2"]) - float(r["x"])) for r in layer["rows"]
    )
    assert area == pytest.approx(1.0)


@altair_available
def test_backend_render_cdf_goes_from_zero_to_one(backend: AltairBackend) -> None:
    chart = backend.render(_panel(CdfSpec(values=np.arange(11.0))))
    y = _column(_layers(chart)[0], "y")
    assert (float(y[0]), float(y[-1])) == (0.0, 1.0)


@altair_available
def test_backend_render_stacked_bar_in_a_layer(backend: AltairBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3), series=(BarSeries(y=np.arange(3)), BarSeries(y=np.arange(3)))
    )
    assert len(_layers(backend.render(_panel(stacked, LINE)))) == 3


@altair_available
def test_backend_render_stacked_bar_uses_the_base(backend: AltairBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.array([1, 2, 3])), BarSeries(y=np.array([4, 5, 6]))),
    )
    assert _column(_layers(backend.render(_panel(stacked)))[1], "y2") == ["1.0", "2.0", "3.0"]


@altair_available
def test_backend_render_layer_draws_every_mark(backend: AltairBackend) -> None:
    chart = backend.render(_panel(LINE, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert [layer["mark"]["type"] for layer in _layers(chart)] == ["line", "point"]


@altair_available
def test_backend_render_slope_alone(backend: AltairBackend) -> None:
    chart = backend.render(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1))
    assert _column(_layers(chart)[0], "y") == ["0.0", "2.0"]


@altair_available
def test_backend_render_slope_in_a_grid(backend: AltairBackend) -> None:
    grid = GridSpec(panels=(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1),))
    assert isinstance(backend.render(grid), alt.ConcatChart)


@altair_available
def test_backend_render_bar_width_is_honored(backend: AltairBackend) -> None:
    chart = backend.render(_panel(BarSpec(x=np.arange(3.0), y=np.arange(3), width=0.5)))
    layer = _layers(chart)[0]
    assert (_column(layer, "x"), _column(layer, "x2")) == (
        ["-0.25", "0.75", "1.75"],
        ["0.25", "1.25", "2.25"],
    )


@altair_available
def test_backend_render_categorical_bar_width_is_a_band_fraction(backend: AltairBackend) -> None:
    chart = backend.render(_panel(BarSpec(x=np.array(["a", "b"]), y=np.arange(2), width=0.5)))
    assert _layers(chart)[0]["mark"]["width"] == {"band": 0.5}


@altair_available
def test_backend_render_categorical_x_order(backend: AltairBackend) -> None:
    chart = backend.render(_panel(BarSpec(x=np.array(["b", "a"]), y=np.arange(2))))
    assert _layers(chart)[0]["encoding"]["x"]["sort"] == ["b", "a"]


@altair_available
def test_backend_render_title(backend: AltairBackend) -> None:
    assert backend.render(_panel(LINE, title="t")).to_dict()["title"] == "t"


@altair_available
def test_backend_render_background_is_the_view_background(backend: AltairBackend) -> None:
    chart = backend.render(_panel(LINE, background_color="red"))
    assert chart.to_dict()["view"] == {"fill": "rgba(255, 0, 0, 1.0)"}


@altair_available
def test_backend_render_every_marker_is_supported(backend: AltairBackend) -> None:
    mark = ScatterSpec(x=np.arange(3), y=np.arange(3), marker="x")
    assert _layers(backend.render(_panel(mark)))[0]["mark"]["shape"] == "M-1,-1L1,1M-1,1L1,-1"


@altair_available
def test_backend_render_grid_is_a_concat(backend: AltairBackend) -> None:
    assert isinstance(
        backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2)), alt.ConcatChart
    )


@altair_available
def test_backend_render_grid_columns(backend: AltairBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2))
    assert grid.to_dict()["columns"] == 2


@altair_available
def test_backend_render_grid_one_view_per_panel(backend: AltairBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2))
    assert len(grid.to_dict()["concat"]) == 3


@altair_available
def test_backend_render_grid_title(backend: AltairBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE),), title="t"))
    assert grid.to_dict()["title"] == "t"


@altair_available
def test_backend_render_grid_background_is_per_panel(backend: AltairBackend) -> None:
    # Regression test: altair rejects a ``background`` inside a concatenated
    # chart, so the background of a panel is the ``view`` background.
    grid = backend.render(GridSpec(panels=(_panel(LINE, background_color="red"),)))
    assert grid.to_dict()["concat"][0]["view"] == {"fill": "rgba(255, 0, 0, 1.0)"}


@altair_available
def test_backend_render_unsupported_legend_location_raises(backend: AltairBackend) -> None:
    scene = AxesScene(primitives=(), legend=LegendStyle(location=cast("Any", "best")))
    with pytest.raises(UnsupportedSpecError, match="does not support legend_location='best'"):
        backend.capabilities().check(scene)


@altair_available
def test_backend_render_does_not_change_the_spec(backend: AltairBackend) -> None:
    spec = _panel(LINE)
    backend.render(spec)
    assert spec == _panel(LINE)


@altair_available
def test_backend_render_large_line_validates_in_constant_time_per_row(
    backend: AltairBackend,
) -> None:
    # Regression test: a list of records is validated row by row against the
    # Vega-Lite schema (3.4 s for 100,000 points), so the data is one CSV string.
    x = np.arange(100_000, dtype=float)
    chart = backend.render(_panel(LineSpec(x=x, y=x)))
    assert len(chart.to_dict()["datasets"]) == 1


@altair_available
def test_backend_draw_axes_scene(backend: AltairBackend) -> None:
    assert isinstance(backend.draw(AxesScene(primitives=())), alt.Chart)


@altair_available
def test_backend_draw_grid_scene(backend: AltairBackend) -> None:
    scene = GridScene(panels=(AxesScene(primitives=()),) * 2, ncols=2)
    assert isinstance(backend.draw(scene), alt.ConcatChart)


# --- save ---


@pytest.mark.parametrize("fmt", ["html", "json"])
@altair_available
def test_backend_save_supported_formats(backend: AltairBackend, tmp_path: Path, fmt: str) -> None:
    path = tmp_path / f"fig.{fmt}"
    backend.save(backend.render(_panel(LINE)), path, fmt)
    assert path.stat().st_size > 0


@altair_available
def test_backend_save_json_is_vega_lite(backend: AltairBackend, tmp_path: Path) -> None:
    path = tmp_path / "fig.json"
    backend.save(backend.render(_panel(LINE)), path, "json")
    assert "vega-lite" in path.read_text(encoding="utf-8")


@altair_available
def test_backend_save_grid(backend: AltairBackend, tmp_path: Path) -> None:
    path = tmp_path / "grid.html"
    backend.save(backend.render(GridSpec(panels=(_panel(LINE),))), path, "html")
    assert path.stat().st_size > 0


@altair_available
def test_backend_show_calls_chart_show(backend: AltairBackend) -> None:
    native = Mock()
    backend.show(native)
    native.show.assert_called_once_with()


###############################
#     Tests for chart_bars    #
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


def _scene_of(*primitives: Any, **kwargs: Any) -> AxesScene:
    return AxesScene(primitives=primitives, **kwargs)


@altair_available
def test_chart_bars_numeric_interval() -> None:
    bars = _bars()
    layer = _layers(chart_bars(bars, _scene_of(bars)))[0]
    assert [_column(layer, c) for c in ("x", "x2", "y", "y2")] == [
        ["0.0", "2.5"],
        ["2.0", "3.5"],
        ["2.0", "5.0"],
        ["0.0", "1.0"],
    ]


@altair_available
def test_chart_bars_encoding() -> None:
    bars = _bars()
    encoding = _layers(chart_bars(bars, _scene_of(bars)))[0]["encoding"]
    assert (encoding["x"]["field"], encoding["x2"]["field"], encoding["y2"]["field"]) == (
        "x",
        "x2",
        "y2",
    )


@altair_available
def test_chart_bars_do_not_stack() -> None:
    bars = _bars()
    assert _layers(chart_bars(bars, _scene_of(bars)))[0]["encoding"]["y"]["stack"] is None


@altair_available
def test_chart_bars_color() -> None:
    bars = _bars()
    assert _layers(chart_bars(bars, _scene_of(bars)))[0]["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_chart_bars_alpha() -> None:
    bars = _bars(alpha=0.5)
    assert _layers(chart_bars(bars, _scene_of(bars)))[0]["mark"]["opacity"] == 0.5


@altair_available
def test_chart_bars_categorical() -> None:
    bars = _bars(x=np.array(["a", "b"]), width=0.5)
    layer = _layers(chart_bars(bars, _scene_of(bars, categories=("a", "b"))))[0]
    assert (_column(layer, "x"), layer["mark"]["width"]) == (["a", "b"], {"band": 0.5})


@altair_available
def test_chart_bars_label_uses_the_legend_color() -> None:
    bars = _bars(label="a")
    layer = _layers(chart_bars(bars, _scene_of(bars, legend=LegendStyle())))[0]
    assert (_column(layer, "label"), layer["encoding"]["color"]["field"]) == (["a", "a"], "label")


@altair_available
def test_chart_bars_label_has_no_fixed_mark_color() -> None:
    bars = _bars(label="a")
    layer = _layers(chart_bars(bars, _scene_of(bars, legend=LegendStyle())))[0]
    assert "color" not in layer["mark"]


@altair_available
def test_chart_bars_without_label_has_no_color_encoding() -> None:
    bars = _bars()
    assert "color" not in _layers(chart_bars(bars, _scene_of(bars)))[0]["encoding"]


###############################
#     Tests for chart_line    #
###############################


def _line(**kwargs: Any) -> Line:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Line(**{**defaults, **kwargs})


@altair_available
def test_chart_line_data() -> None:
    line = _line()
    layer = _layers(chart_line(line, _scene_of(line)))[0]
    assert (layer["mark"]["type"], _column(layer, "x"), _column(layer, "y")) == (
        "line",
        ["0.0", "1.0"],
        ["2.0", "3.0"],
    )


@altair_available
def test_chart_line_style() -> None:
    line = _line(alpha=0.5, linewidth=3.0, linestyle="dashed")
    mark = _layers(chart_line(line, _scene_of(line)))[0]["mark"]
    assert (mark["opacity"], mark["strokeWidth"], mark["strokeDash"]) == (0.5, 3.0, [6, 4])


@altair_available
def test_chart_line_solid_has_no_dash() -> None:
    line = _line()
    assert "strokeDash" not in _layers(chart_line(line, _scene_of(line)))[0]["mark"]


@altair_available
def test_chart_line_color() -> None:
    line = _line()
    assert _layers(chart_line(line, _scene_of(line)))[0]["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_chart_line_nan_is_an_empty_cell() -> None:
    line = _line(y=np.array([1.0, np.nan]))
    assert _column(_layers(chart_line(line, _scene_of(line)))[0], "y") == ["1.0", ""]


@altair_available
def test_chart_line_infinite_is_the_segment() -> None:
    line = _line(infinite=(2.0, 1.0))
    assert _column(_layers(chart_line(line, _scene_of(line)))[0], "x") == ["0.0", "1.0"]


@altair_available
def test_chart_line_label_uses_the_legend_color() -> None:
    line = _line(label="a")
    layer = _layers(chart_line(line, _scene_of(line, legend=LegendStyle())))[0]
    assert layer["encoding"]["color"]["scale"] == {
        "domain": ["a"],
        "range": ["rgba(255, 0, 0, 1.0)"],
    }


@altair_available
def test_chart_line_categorical_x() -> None:
    line = _line(x=np.array(["a", "b"]))
    layer = _layers(chart_line(line, _scene_of(line, categories=("a", "b"))))[0]
    assert layer["encoding"]["x"]["type"] == "nominal"


#################################
#     Tests for chart_points    #
#################################


def _points(**kwargs: Any) -> Points:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Points(**{**defaults, **kwargs})


def _point_mark(**kwargs: Any) -> dict[str, Any]:
    points = _points(**kwargs)
    return _layers(chart_points(points, _scene_of(points)))[0]["mark"]


@altair_available
def test_chart_points_data() -> None:
    points = _points()
    layer = _layers(chart_points(points, _scene_of(points)))[0]
    assert (layer["mark"]["type"], _column(layer, "x")) == ("point", ["0.0", "1.0"])


@altair_available
def test_chart_points_color() -> None:
    assert _point_mark()["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_chart_points_size() -> None:
    assert _point_mark(size=7.0)["size"] == 7.0


@altair_available
def test_chart_points_alpha() -> None:
    assert _point_mark(alpha=0.5)["opacity"] == 0.5


@altair_available
def test_chart_points_marker() -> None:
    assert _point_mark(marker="triangle")["shape"] == "triangle-up"


@altair_available
def test_chart_points_cross_x_is_an_open_path() -> None:
    mark = _point_mark(marker="x")
    assert (mark["shape"], mark["filled"]) == ("M-1,-1L1,1M-1,1L1,-1", False)


@altair_available
def test_chart_points_edgecolor() -> None:
    mark = _point_mark(edgecolor=BLUE)
    assert (mark["stroke"], mark["filled"]) == ("rgba(0, 0, 255, 1.0)", True)


@altair_available
def test_chart_points_hollow() -> None:
    assert _point_mark(fill=False)["filled"] is False


@altair_available
def test_chart_points_fill_true_does_not_set_filled() -> None:
    assert "filled" not in _point_mark(fill=True)


@altair_available
def test_chart_points_label_uses_the_legend_color() -> None:
    points = _points(label="a")
    layer = _layers(chart_points(points, _scene_of(points, legend=LegendStyle())))[0]
    assert layer["encoding"]["color"]["field"] == "label"


##########################################
#     Tests for _chart/_mark_chart/etc   #
##########################################


@altair_available
def test_chart_bars() -> None:
    bars = _bars()
    assert _layers(_chart(bars, _scene_of(bars)))[0]["mark"]["type"] == "bar"


@altair_available
def test_chart_line() -> None:
    line = _line()
    assert _layers(_chart(line, _scene_of(line)))[0]["mark"]["type"] == "line"


@altair_available
def test_chart_points() -> None:
    points = _points()
    assert _layers(_chart(points, _scene_of(points)))[0]["mark"]["type"] == "point"


@altair_available
def test_mark_chart_label_adds_a_label_column() -> None:
    chart = _mark_chart({"x": np.array([0.0, 1.0])}, "line", "a", {})
    assert _column(_layers(chart)[0], "label") == ["a", "a"]


@altair_available
def test_mark_chart_without_label_has_no_label_column() -> None:
    chart = _mark_chart({"x": np.array([0.0, 1.0])}, "line", None, {})
    assert "label" not in _layers(chart)[0]["rows"][0]


@altair_available
def test_mark_chart_properties() -> None:
    chart = _mark_chart({"x": np.array([0.0])}, "line", None, {"strokeWidth": 2})
    assert chart.to_dict()["mark"] == {"type": "line", "strokeWidth": 2}


@altair_available
def test_empty_chart() -> None:
    assert _empty_chart().to_dict()["mark"]["type"] == "point"


@altair_available
def test_draw_axes_one_primitive_is_not_a_layer() -> None:
    line = _line()
    assert "layer" not in _draw_axes(_scene_of(line)).to_dict()


@altair_available
def test_draw_axes_layers_the_primitives_in_order() -> None:
    scene = _scene_of(_line(), _points())
    assert [layer["mark"]["type"] for layer in _layers(_draw_axes(scene))] == ["line", "point"]


@altair_available
def test_draw_axes_without_primitive() -> None:
    assert _draw_axes(_scene_of()).to_dict()["mark"]["type"] == "point"


@altair_available
def test_draw_axes_title() -> None:
    assert _draw_axes(_scene_of(_line(), title="t")).to_dict()["title"] == "t"


@altair_available
def test_draw_axes_no_title() -> None:
    assert "title" not in _draw_axes(_scene_of(_line())).to_dict()


@altair_available
def test_draw_axes_no_background() -> None:
    assert "view" not in _draw_axes(_scene_of(_line())).to_dict()
