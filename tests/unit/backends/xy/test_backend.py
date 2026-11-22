from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import UnsupportedFormatError, UnsupportedSpecError
from plotmux.primitives import Bars, Line, Points
from plotmux.scene import AxesScene, GridScene, LegendStyle
from plotmux.specs import (
    BarSeries,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.backend import (
        XyBackend,
        _draw_axes,
        _mark,
        mark_bars,
        mark_line,
        mark_points,
    )
    from plotmux.backends.xy.grid import XyGrid


@pytest.fixture
def backend() -> XyBackend:
    return XyBackend()


def _panel(*marks: Any, **kwargs: Any) -> PanelSpec:
    return PanelSpec(marks=marks, **kwargs)


def _marks(chart: Any) -> list[Any]:
    return [c for c in chart.children if type(c).__name__ == "Mark"]


LINE = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
RED = (1.0, 0.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

#############################
#     Tests for XyBackend   #
#############################


@xy_available
def test_backend_name(backend: XyBackend) -> None:
    assert backend.name == "xy"


@xy_available
def test_backend_capabilities_formats(backend: XyBackend) -> None:
    assert backend.capabilities().formats == frozenset(
        {"png", "jpg", "jpeg", "webp", "svg", "pdf", "html"}
    )


@xy_available
def test_backend_capabilities_grid_formats_are_html_only(backend: XyBackend) -> None:
    assert backend.capabilities().grid_formats == frozenset({"html"})


@xy_available
def test_backend_capabilities_legend_locations(backend: XyBackend) -> None:
    assert backend.capabilities().legend_locations == frozenset(
        {"top_left", "top_right", "bottom_left", "bottom_right", "top", "bottom", "left", "right"}
    )


@xy_available
def test_backend_capabilities_markers(backend: XyBackend) -> None:
    assert backend.capabilities().markers == frozenset(
        {"circle", "square", "triangle", "diamond", "cross", "x"}
    )


# --- render ---


@xy_available
def test_backend_render_returns_a_chart(backend: XyBackend) -> None:
    assert isinstance(backend.render(_panel(LINE)), Chart)


@xy_available
def test_backend_render_histogram_has_one_bar_per_bin(backend: XyBackend) -> None:
    chart = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10)))
    assert _marks(chart)[0].x.shape == (10,)


@xy_available
def test_backend_render_histogram_density_integrates_to_one(backend: XyBackend) -> None:
    chart = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10, density=True)))
    mark = _marks(chart)[0]
    assert float((mark.y * mark.props["width"]).sum()) == pytest.approx(1.0)


@xy_available
def test_backend_render_cdf_goes_from_zero_to_one(backend: XyBackend) -> None:
    chart = backend.render(_panel(CdfSpec(values=np.arange(11.0))))
    y = _marks(chart)[0].y
    assert (y[0], y[-1]) == (0.0, 1.0)


@xy_available
def test_backend_render_stacked_bar_in_a_layer(backend: XyBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3), series=(BarSeries(y=np.arange(3)), BarSeries(y=np.arange(3)))
    )
    assert len(_marks(backend.render(_panel(stacked, LINE)))) == 3


@xy_available
def test_backend_render_stacked_bar_uses_the_base(backend: XyBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.array([1, 2, 3])), BarSeries(y=np.array([4, 5, 6]))),
    )
    assert _marks(backend.render(_panel(stacked)))[1].props["base"].tolist() == [1.0, 2.0, 3.0]


@xy_available
def test_backend_render_layer_draws_every_mark(backend: XyBackend) -> None:
    chart = backend.render(_panel(LINE, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert [m.kind for m in _marks(chart)] == ["line", "scatter"]


@xy_available
def test_backend_render_slope_alone(backend: XyBackend) -> None:
    chart = backend.render(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1))
    assert _marks(chart)[0].y.tolist() == [0.0, 2.0]


@xy_available
def test_backend_render_slope_in_a_grid(backend: XyBackend) -> None:
    grid = GridSpec(panels=(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1),))
    assert len(backend.render(grid).charts) == 1


@xy_available
def test_backend_render_applies_the_axes_style(backend: XyBackend) -> None:
    assert backend.render(_panel(LINE, title="t")).title == "t"


@xy_available
def test_backend_render_grid_returns_an_xy_grid(backend: XyBackend) -> None:
    assert isinstance(backend.render(GridSpec(panels=(_panel(LINE),))), XyGrid)


@xy_available
def test_backend_render_grid_one_chart_per_panel(backend: XyBackend) -> None:
    assert len(backend.render(GridSpec(panels=(_panel(LINE), _panel(LINE)), ncols=2)).charts) == 2


@xy_available
def test_backend_render_grid_layout(backend: XyBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE),), ncols=3, title="t"))
    assert (grid.ncols, grid.title) == (3, "t")


@xy_available
def test_backend_render_styles_each_grid_panel(backend: XyBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE, title="a"), _panel(LINE, title="b"))))
    assert [chart.title for chart in grid.charts] == ["a", "b"]


@xy_available
def test_backend_render_every_marker_is_supported(backend: XyBackend) -> None:
    mark = ScatterSpec(x=np.arange(3), y=np.arange(3), marker="x")
    assert _marks(backend.render(_panel(mark)))[0].props["symbol"] == "x"


@xy_available
def test_backend_render_unsupported_legend_location_raises(backend: XyBackend) -> None:
    scene = AxesScene(primitives=(), legend=LegendStyle(location=cast("Any", "best")))
    with pytest.raises(UnsupportedSpecError, match="does not support legend_location='best'"):
        backend.capabilities().check(scene)


@xy_available
def test_backend_render_does_not_change_the_spec(backend: XyBackend) -> None:
    spec = _panel(LINE)
    backend.render(spec)
    assert spec == _panel(LINE)


@xy_available
def test_backend_draw_axes_scene(backend: XyBackend) -> None:
    assert isinstance(backend.draw(AxesScene(primitives=())), Chart)


@xy_available
def test_backend_draw_grid_scene(backend: XyBackend) -> None:
    scene = GridScene(panels=(AxesScene(primitives=()),) * 2, ncols=2)
    assert len(cast("XyGrid", backend.draw(scene)).charts) == 2


# --- save ---


@pytest.mark.parametrize("fmt", ["png", "svg", "html"])
@xy_available
def test_backend_save_supported_formats(backend: XyBackend, tmp_path: Path, fmt: str) -> None:
    path = tmp_path / f"fig.{fmt}"
    backend.save(backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10))), path, fmt)
    assert path.is_file()


@xy_available
def test_backend_save_grid_html(backend: XyBackend, tmp_path: Path) -> None:
    path = tmp_path / "fig.html"
    backend.save(backend.render(GridSpec(panels=(_panel(LINE),))), path, "html")
    assert path.stat().st_size > 0


@xy_available
def test_backend_save_grid_unsupported_format(backend: XyBackend, tmp_path: Path) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),)))
    with pytest.raises(UnsupportedFormatError, match="does not support exporting a grid to 'png'"):
        backend.save(native, tmp_path / "fig.png", "png")


@xy_available
def test_backend_save_grid_unsupported_format_writes_nothing(
    backend: XyBackend, tmp_path: Path
) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),)))
    with pytest.raises(UnsupportedFormatError, match="grid"):
        backend.save(native, tmp_path / "fig.png", "png")
    assert not (tmp_path / "fig.png").exists()


# --- show ---


@xy_available
def test_backend_show_opens_the_html_in_the_browser(
    backend: XyBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url) or True)
    backend.show(backend.render(_panel(LINE)))
    assert opened[0].endswith(".html")


@xy_available
def test_backend_show_writes_the_html_of_a_grid(
    backend: XyBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url) or True)
    backend.show(backend.render(GridSpec(panels=(_panel(LINE),))))
    assert "<html" in Path(opened[0].removeprefix("file://")).read_text(encoding="utf-8")


# --- mimebundle ---


@xy_available
def test_backend_mimebundle_chart(backend: XyBackend) -> None:
    bundle = backend.mimebundle(backend.render(_panel(LINE)))
    assert list(cast("dict[str, Any]", bundle)) == ["text/html"]


@xy_available
def test_backend_mimebundle_grid(backend: XyBackend) -> None:
    bundle = backend.mimebundle(backend.render(GridSpec(panels=(_panel(LINE),))))
    assert "<iframe" in cast("dict[str, Any]", bundle)["text/html"]


#################################
#     Tests for mark_bars       #
#################################


def _bars(**kwargs: Any) -> Bars:
    defaults: dict[str, Any] = {
        "x": np.array([1.0, 3.0]),
        "height": np.array([2.0, 4.0]),
        "base": np.array([0.0, 1.0]),
        "width": np.array([2.0, 1.0]),
        "color": RED,
    }
    return Bars(**{**defaults, **kwargs})


@xy_available
def test_mark_bars_data() -> None:
    mark = mark_bars(_bars())
    assert (mark.kind, mark.x.tolist(), mark.y.tolist()) == ("bar", [1.0, 3.0], [2.0, 4.0])


@xy_available
def test_mark_bars_array_width() -> None:
    assert mark_bars(_bars()).props["width"].tolist() == [2.0, 1.0]


@xy_available
def test_mark_bars_scalar_width() -> None:
    assert mark_bars(_bars(width=0.5)).props["width"] == 0.5


@xy_available
def test_mark_bars_base() -> None:
    assert mark_bars(_bars()).props["base"].tolist() == [0.0, 1.0]


@xy_available
def test_mark_bars_color() -> None:
    assert mark_bars(_bars()).props["color"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_mark_bars_alpha() -> None:
    assert mark_bars(_bars(alpha=0.5)).props["opacity"] == 0.5


@xy_available
def test_mark_bars_default_opacity() -> None:
    assert mark_bars(_bars()).props["opacity"] == 0.85


@xy_available
def test_mark_bars_label() -> None:
    assert mark_bars(_bars(label="a")).name == "a"


@xy_available
def test_mark_bars_categorical() -> None:
    assert mark_bars(_bars(x=np.array(["a", "b"]))).x.tolist() == ["a", "b"]


@xy_available
def test_mark_bars_without_color() -> None:
    assert mark_bars(_bars(color=None)).props["color"] is None


#################################
#     Tests for mark_line       #
#################################


def _line(**kwargs: Any) -> Line:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Line(**{**defaults, **kwargs})


@xy_available
def test_mark_line_data() -> None:
    mark = mark_line(_line())
    assert (mark.kind, mark.x.tolist(), mark.y.tolist()) == ("line", [0.0, 1.0], [2.0, 3.0])


@xy_available
def test_mark_line_color() -> None:
    assert mark_line(_line()).props["color"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_mark_line_style() -> None:
    props = mark_line(_line(alpha=0.5, linewidth=3.0, linestyle="dashed")).props
    assert (props["opacity"], props["width"], props["dash"]) == (0.5, 3.0, "dashed")


@xy_available
def test_mark_line_solid_has_no_dash() -> None:
    assert mark_line(_line()).props["dash"] is None


@xy_available
def test_mark_line_label() -> None:
    assert mark_line(_line(label="a")).name == "a"


@xy_available
def test_mark_line_infinite_is_the_segment() -> None:
    assert mark_line(_line(infinite=(2.0, 1.0))).x.tolist() == [0.0, 1.0]


@xy_available
def test_mark_line_nan_is_kept() -> None:
    assert np.isnan(mark_line(_line(y=np.array([1.0, np.nan]))).y[1])


@xy_available
def test_mark_line_without_color() -> None:
    assert mark_line(_line(color=None)).props["color"] is None


###################################
#     Tests for mark_points       #
###################################


def _points(**kwargs: Any) -> Points:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Points(**{**defaults, **kwargs})


@xy_available
def test_mark_points_data() -> None:
    mark = mark_points(_points())
    assert (mark.kind, mark.x.tolist(), mark.y.tolist()) == ("scatter", [0.0, 1.0], [2.0, 3.0])


@xy_available
def test_mark_points_color() -> None:
    assert mark_points(_points()).props["color"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_mark_points_size() -> None:
    assert mark_points(_points(size=7.0)).props["size"] == 7.0


@xy_available
def test_mark_points_default_size() -> None:
    assert mark_points(_points()).props["size"] == 4.0


@xy_available
def test_mark_points_alpha() -> None:
    assert mark_points(_points(alpha=0.5)).props["opacity"] == 0.5


@xy_available
def test_mark_points_marker() -> None:
    assert mark_points(_points(marker="square")).props["symbol"] == "square"


@xy_available
def test_mark_points_default_marker_is_a_circle() -> None:
    assert mark_points(_points()).props["symbol"] == "circle"


@xy_available
def test_mark_points_edgecolor() -> None:
    props = mark_points(_points(edgecolor=BLUE)).props
    assert (props["stroke"], props["stroke_width"]) == ("rgba(0, 0, 255, 1.0)", 1.0)


@xy_available
def test_mark_points_hollow_is_transparent() -> None:
    assert mark_points(_points(fill=False)).props["color"] == "rgba(0, 0, 0, 0)"


@xy_available
def test_mark_points_hollow_outline_is_the_color() -> None:
    assert mark_points(_points(fill=False)).props["stroke"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_mark_points_hollow_outline_is_the_edgecolor() -> None:
    props = mark_points(_points(fill=False, edgecolor=BLUE)).props
    assert props["stroke"] == "rgba(0, 0, 255, 1.0)"


@xy_available
def test_mark_points_fill_true_is_filled() -> None:
    assert mark_points(_points(fill=True)).props["color"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_mark_points_label() -> None:
    assert mark_points(_points(label="a")).name == "a"


####################################
#     Tests for _mark/_draw_axes   #
####################################


@xy_available
def test_mark_bars() -> None:
    assert _mark(_bars()).kind == "bar"


@xy_available
def test_mark_line() -> None:
    assert _mark(_line()).kind == "line"


@xy_available
def test_mark_points() -> None:
    assert _mark(_points()).kind == "scatter"


@xy_available
def test_draw_axes_marks_follow_the_primitives() -> None:
    chart = _draw_axes(AxesScene(primitives=(_line(), _points())))
    assert [m.kind for m in _marks(chart)] == ["line", "scatter"]


@xy_available
def test_draw_axes_applies_the_style() -> None:
    assert _draw_axes(AxesScene(primitives=(_line(),), title="t")).title == "t"
