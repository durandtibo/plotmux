from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

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
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if TYPE_CHECKING:
    from pathlib import Path

if is_bokeh_available():
    from bokeh.models import Column, GridPlot, LogScale, Slope
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.backend import (
        BokehBackend,
        _draw_axes,
        _draw_primitive,
        draw_bars,
        draw_line,
        draw_points,
    )


@pytest.fixture
def backend() -> BokehBackend:
    return BokehBackend()


def _figure(**kwargs: Any) -> Any:
    return figure(**kwargs)


def _panel(*marks: Any, **kwargs: Any) -> PanelSpec:
    return PanelSpec(marks=marks, **kwargs)


def _glyphs(fig: Any) -> list[Any]:
    return [r.glyph for r in fig.renderers]


def _data(fig: Any, index: int = 0) -> dict[str, Any]:
    return dict(fig.renderers[index].data_source.data)


LINE = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
RED = (1.0, 0.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

###############################
#     Tests for BokehBackend  #
###############################


@bokeh_available
def test_backend_name(backend: BokehBackend) -> None:
    assert backend.name == "bokeh"


@bokeh_available
def test_backend_capabilities_formats(backend: BokehBackend) -> None:
    assert backend.capabilities().formats == frozenset({"html"})


@bokeh_available
def test_backend_capabilities_grid_formats(backend: BokehBackend) -> None:
    assert backend.capabilities().grid_formats == frozenset({"html"})


@bokeh_available
def test_backend_capabilities_legend_locations(backend: BokehBackend) -> None:
    assert backend.capabilities().legend_locations == frozenset(
        {"top_left", "top_right", "bottom_left", "bottom_right", "top", "bottom", "left", "right"}
    )


@bokeh_available
def test_backend_capabilities_markers(backend: BokehBackend) -> None:
    assert backend.capabilities().markers == frozenset(
        {"circle", "square", "triangle", "diamond", "cross", "x"}
    )


# --- render ---


@bokeh_available
def test_backend_render_returns_a_figure(backend: BokehBackend) -> None:
    assert isinstance(backend.render(_panel(LINE)), figure)


@bokeh_available
def test_backend_render_histogram_has_one_bar_per_bin(backend: BokehBackend) -> None:
    fig = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10)))
    assert len(_data(fig)["x"]) == 10


@bokeh_available
def test_backend_render_histogram_density_integrates_to_one(backend: BokehBackend) -> None:
    fig = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10, density=True)))
    data = _data(fig)
    assert float((data["top"] * data["width"]).sum()) == pytest.approx(1.0)


@bokeh_available
def test_backend_render_cdf_goes_from_zero_to_one(backend: BokehBackend) -> None:
    fig = backend.render(_panel(CdfSpec(values=np.arange(11.0))))
    y = _data(fig)["y"]
    assert (y[0], y[-1]) == (0.0, 1.0)


@bokeh_available
def test_backend_render_stacked_bar_in_a_layer(backend: BokehBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3), series=(BarSeries(y=np.arange(3)), BarSeries(y=np.arange(3)))
    )
    assert len(backend.render(_panel(stacked, LINE)).renderers) == 3


@bokeh_available
def test_backend_render_stacked_bar_uses_the_base(backend: BokehBackend) -> None:
    stacked = StackedBarSpec(
        x=np.arange(3),
        series=(BarSeries(y=np.array([1, 2, 3])), BarSeries(y=np.array([4, 5, 6]))),
    )
    fig = backend.render(_panel(stacked))
    assert _data(fig, 1)["bottom"].tolist() == [1.0, 2.0, 3.0]


@bokeh_available
def test_backend_render_layer_draws_every_mark(backend: BokehBackend) -> None:
    fig = backend.render(_panel(LINE, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert [type(g).__name__ for g in _glyphs(fig)] == ["Line", "Scatter"]


@bokeh_available
def test_backend_render_slope_alone(backend: BokehBackend) -> None:
    fig = backend.render(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1))
    assert [type(c).__name__ for c in fig.center if isinstance(c, Slope)] == ["Slope"]


@bokeh_available
def test_backend_render_slope_in_a_grid(backend: BokehBackend) -> None:
    grid = GridSpec(panels=(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1),))
    assert isinstance(backend.render(grid), GridPlot)


@bokeh_available
def test_backend_render_categorical_x_range(backend: BokehBackend) -> None:
    fig = backend.render(_panel(BarSpec(x=np.array(["b", "a"]), y=np.arange(2))))
    assert list(fig.x_range.factors) == ["b", "a"]


@bokeh_available
def test_backend_render_log_scales(backend: BokehBackend) -> None:
    fig = backend.render(_panel(LINE, xscale="log", yscale="log"))
    assert isinstance(fig.x_scale, LogScale)


@bokeh_available
def test_backend_render_log_y_with_categorical_x(backend: BokehBackend) -> None:
    fig = backend.render(_panel(BarSpec(x=np.array(["a", "b"]), y=np.array([1, 2])), yscale="log"))
    assert isinstance(fig.y_scale, LogScale)


@bokeh_available
def test_backend_render_applies_the_axes_style(backend: BokehBackend) -> None:
    assert backend.render(_panel(LINE, title="t")).title.text == "t"


@bokeh_available
def test_backend_render_grid_is_a_gridplot(backend: BokehBackend) -> None:
    assert isinstance(backend.render(GridSpec(panels=(_panel(LINE),))), GridPlot)


@bokeh_available
def test_backend_render_grid_with_title_is_a_column(backend: BokehBackend) -> None:
    assert isinstance(backend.render(GridSpec(panels=(_panel(LINE),), title="t")), Column)


@bokeh_available
def test_backend_render_grid_title_is_escaped(backend: BokehBackend) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),), title="a <b>"))
    assert native.children[0].text == "<h2>a &lt;b&gt;</h2>"


@bokeh_available
def test_backend_render_grid_one_figure_per_panel(backend: BokehBackend) -> None:
    grid = backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2))
    assert len(grid.children) == 3


@bokeh_available
def test_backend_render_every_marker_is_supported(backend: BokehBackend) -> None:
    mark = ScatterSpec(x=np.arange(3), y=np.arange(3), marker="x")
    assert backend.render(_panel(mark)).renderers[0].glyph.marker == "x"


@bokeh_available
def test_backend_render_unsupported_legend_location_raises(backend: BokehBackend) -> None:
    scene = AxesScene(primitives=(), legend=LegendStyle(location=cast("Any", "best")))
    with pytest.raises(UnsupportedSpecError, match="does not support legend_location='best'"):
        backend.capabilities().check(scene)


@bokeh_available
def test_backend_render_does_not_change_the_spec(backend: BokehBackend) -> None:
    spec = _panel(LINE)
    backend.render(spec)
    assert spec == _panel(LINE)


@bokeh_available
def test_backend_draw_axes_scene(backend: BokehBackend) -> None:
    assert isinstance(backend.draw(AxesScene(primitives=())), figure)


@bokeh_available
def test_backend_draw_grid_scene(backend: BokehBackend) -> None:
    scene = GridScene(panels=(AxesScene(primitives=()),) * 2, ncols=2)
    assert isinstance(backend.draw(scene), GridPlot)


# --- save ---


@bokeh_available
def test_backend_save_html(backend: BokehBackend, tmp_path: Path) -> None:
    path = tmp_path / "fig.html"
    backend.save(backend.render(_panel(LINE)), path, "html")
    assert path.stat().st_size > 0


@bokeh_available
def test_backend_save_title_is_the_figure_title(backend: BokehBackend, tmp_path: Path) -> None:
    path = tmp_path / "fig.html"
    backend.save(backend.render(_panel(LINE, title="my-title")), path, "html")
    assert "<title>my-title</title>" in path.read_text(encoding="utf-8")


@bokeh_available
def test_backend_save_grid_with_title(backend: BokehBackend, tmp_path: Path) -> None:
    # Regression test: the ``column`` layout of a grid has no ``.title``
    # attribute at all (unlike a plain ``figure``), so ``save`` must not
    # assume one is always present.
    path = tmp_path / "grid.html"
    backend.save(backend.render(GridSpec(panels=(_panel(LINE),), title="overall")), path, "html")
    assert path.stat().st_size > 0


# --- show ---


@bokeh_available
def test_backend_show_calls_bokeh_show(
    backend: BokehBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    shown: list[Any] = []
    monkeypatch.setattr("plotmux.backends.bokeh.backend.bokeh_show", shown.append)
    native = backend.render(_panel(LINE))
    backend.show(native)
    assert shown == [native]


################################
#     Tests for draw_bars      #
################################


def _bars(**kwargs: Any) -> Bars:
    defaults: dict[str, Any] = {
        "x": np.array([1.0, 3.0]),
        "height": np.array([2.0, 4.0]),
        "base": np.array([0.0, 1.0]),
        "width": 0.5,
        "color": RED,
    }
    return Bars(**{**defaults, **kwargs})


@bokeh_available
def test_draw_bars_data() -> None:
    fig = _figure()
    draw_bars(fig, _bars())
    data = _data(fig)
    assert (data["x"].tolist(), data["bottom"].tolist(), data["top"].tolist()) == (
        [1.0, 3.0],
        [0.0, 1.0],
        [2.0, 5.0],
    )


@bokeh_available
def test_draw_bars_scalar_width() -> None:
    fig = _figure()
    draw_bars(fig, _bars())
    assert fig.renderers[0].glyph.width == 0.5


@bokeh_available
def test_draw_bars_array_width() -> None:
    fig = _figure()
    draw_bars(fig, _bars(width=np.array([2.0, 1.0])))
    assert _data(fig)["width"].tolist() == [2.0, 1.0]


@bokeh_available
def test_draw_bars_color() -> None:
    fig = _figure()
    draw_bars(fig, _bars())
    assert fig.renderers[0].glyph.fill_color == (255, 0, 0, 1.0)


@bokeh_available
def test_draw_bars_alpha() -> None:
    fig = _figure()
    draw_bars(fig, _bars(alpha=0.5))
    assert fig.renderers[0].glyph.fill_alpha == 0.5


@bokeh_available
def test_draw_bars_label() -> None:
    fig = _figure()
    draw_bars(fig, _bars(label="a"))
    assert fig.legend[0].items[0].label.value == "a"


@bokeh_available
def test_draw_bars_without_label_has_no_legend() -> None:
    fig = _figure()
    draw_bars(fig, _bars())
    assert len(fig.legend) == 0


@bokeh_available
def test_draw_bars_categorical() -> None:
    fig = _figure(x_range=["a", "b"])
    draw_bars(fig, _bars(x=np.array(["a", "b"])))
    assert _data(fig)["x"].tolist() == ["a", "b"]


@bokeh_available
def test_draw_bars_does_not_change_the_primitive() -> None:
    bars = _bars()
    draw_bars(_figure(), bars)
    assert bars == _bars()


################################
#     Tests for draw_line      #
################################


def _line(**kwargs: Any) -> Line:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Line(**{**defaults, **kwargs})


@bokeh_available
def test_draw_line_data() -> None:
    fig = _figure()
    draw_line(fig, _line())
    assert _data(fig)["y"].tolist() == [2.0, 3.0]


@bokeh_available
def test_draw_line_style() -> None:
    fig = _figure()
    draw_line(fig, _line(alpha=0.5, linewidth=3.0, linestyle="dashed"))
    glyph = fig.renderers[0].glyph
    assert (glyph.line_alpha, glyph.line_width, glyph.line_dash) == (0.5, 3.0, [6])


@bokeh_available
def test_draw_line_color() -> None:
    fig = _figure()
    draw_line(fig, _line())
    assert fig.renderers[0].glyph.line_color == "rgb(255, 0, 0)"


@bokeh_available
def test_draw_line_label() -> None:
    fig = _figure()
    draw_line(fig, _line(label="a"))
    assert fig.legend[0].items[0].label.value == "a"


@bokeh_available
def test_draw_line_infinite_is_a_slope_annotation() -> None:
    fig = _figure()
    draw_line(fig, _line(infinite=(2.0, 1.0)))
    (slope,) = [c for c in fig.center if isinstance(c, Slope)]
    assert (slope.gradient, slope.y_intercept) == (2.0, 1.0)


@bokeh_available
def test_draw_line_infinite_adds_no_glyph() -> None:
    fig = _figure()
    draw_line(fig, _line(infinite=(2.0, 1.0)))
    assert len(fig.renderers) == 0


@bokeh_available
def test_draw_line_infinite_style() -> None:
    fig = _figure()
    draw_line(fig, _line(infinite=(2.0, 1.0), alpha=0.5, linewidth=3.0))
    (slope,) = [c for c in fig.center if isinstance(c, Slope)]
    assert (slope.line_alpha, slope.line_width, slope.line_color) == (0.5, 3.0, "rgb(255, 0, 0)")


@bokeh_available
def test_draw_line_infinite_with_a_label_is_the_segment() -> None:
    # A ``Slope`` has no legend entry: a labeled slope is drawn as its segment.
    fig = _figure()
    draw_line(fig, _line(infinite=(2.0, 1.0), label="a"))
    assert fig.legend[0].items[0].label.value == "a"


@bokeh_available
def test_draw_line_infinite_with_a_label_adds_no_annotation() -> None:
    fig = _figure()
    draw_line(fig, _line(infinite=(2.0, 1.0), label="a"))
    assert [c for c in fig.center if isinstance(c, Slope)] == []


################################
#     Tests for draw_points    #
################################


def _points(**kwargs: Any) -> Points:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Points(**{**defaults, **kwargs})


@bokeh_available
def test_draw_points_data() -> None:
    fig = _figure()
    draw_points(fig, _points())
    assert _data(fig)["x"].tolist() == [0.0, 1.0]


@bokeh_available
def test_draw_points_color() -> None:
    fig = _figure()
    draw_points(fig, _points())
    glyph = fig.renderers[0].glyph
    assert (glyph.fill_color, glyph.line_color) == ((255, 0, 0, 1.0), (255, 0, 0, 1.0))


@bokeh_available
def test_draw_points_size() -> None:
    fig = _figure()
    draw_points(fig, _points(size=7.0))
    assert fig.renderers[0].glyph.size == 7.0


@bokeh_available
def test_draw_points_alpha() -> None:
    fig = _figure()
    draw_points(fig, _points(alpha=0.5))
    assert fig.renderers[0].glyph.fill_alpha == 0.5


@bokeh_available
def test_draw_points_marker() -> None:
    fig = _figure()
    draw_points(fig, _points(marker="square"))
    assert fig.renderers[0].glyph.marker == "square"


@bokeh_available
def test_draw_points_label() -> None:
    fig = _figure()
    draw_points(fig, _points(label="a"))
    assert fig.legend[0].items[0].label.value == "a"


@bokeh_available
def test_draw_points_edgecolor() -> None:
    fig = _figure()
    draw_points(fig, _points(edgecolor=BLUE))
    assert fig.renderers[0].glyph.line_color == (0, 0, 255, 1.0)


@bokeh_available
def test_draw_points_hollow_has_no_fill() -> None:
    fig = _figure()
    draw_points(fig, _points(fill=False))
    assert fig.renderers[0].glyph.fill_color is None


@bokeh_available
def test_draw_points_hollow_outline_is_the_color() -> None:
    fig = _figure()
    draw_points(fig, _points(fill=False))
    assert fig.renderers[0].glyph.line_color == (255, 0, 0, 1.0)


@bokeh_available
def test_draw_points_fill_true_is_filled() -> None:
    fig = _figure()
    draw_points(fig, _points(fill=True))
    assert fig.renderers[0].glyph.fill_color == (255, 0, 0, 1.0)


####################################
#     Tests for _draw_primitive    #
####################################


@bokeh_available
def test_draw_primitive_bars() -> None:
    fig = _figure()
    _draw_primitive(fig, _bars())
    assert type(fig.renderers[0].glyph).__name__ == "VBar"


@bokeh_available
def test_draw_primitive_line() -> None:
    fig = _figure()
    _draw_primitive(fig, _line())
    assert type(fig.renderers[0].glyph).__name__ == "Line"


@bokeh_available
def test_draw_primitive_points() -> None:
    fig = _figure()
    _draw_primitive(fig, _points())
    assert type(fig.renderers[0].glyph).__name__ == "Scatter"


##############################
#     Tests for _draw_axes   #
##############################


@bokeh_available
def test_draw_axes_draws_in_order() -> None:
    fig = _draw_axes(AxesScene(primitives=(_line(), _points())))
    assert [type(g).__name__ for g in _glyphs(fig)] == ["Line", "Scatter"]


@bokeh_available
def test_draw_axes_applies_the_style() -> None:
    assert cast("Any", _draw_axes(AxesScene(primitives=(), title="t"))).title.text == "t"


@bokeh_available
def test_draw_axes_categories_are_the_x_range() -> None:
    fig = cast("Any", _draw_axes(AxesScene(primitives=(), categories=("b", "a"))))
    assert list(fig.x_range.factors) == ["b", "a"]


@bokeh_available
def test_draw_axes_legend_style() -> None:
    scene = AxesScene(primitives=(_line(label="a"),), legend=LegendStyle(title="l"))
    assert _draw_axes(scene).legend[0].title == "l"


@bokeh_available
def test_draw_bars_without_color_keeps_the_default() -> None:
    fig = _figure()
    draw_bars(fig, _bars(color=None))
    assert fig.renderers[0].glyph.fill_color != (255, 0, 0, 1.0)


@bokeh_available
def test_draw_line_without_color_keeps_the_default() -> None:
    fig = _figure()
    draw_line(fig, _line(color=None))
    assert fig.renderers[0].glyph.line_color != (255, 0, 0, 1.0)
