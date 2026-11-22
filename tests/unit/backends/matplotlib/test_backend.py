from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, cast

import numpy as np
import pytest

from plotmux.exceptions import UnsupportedSpecError
from plotmux.primitives import Bars, Line, Points
from plotmux.scene import AxesScene, GridScene, LegendStyle
from plotmux.specs import (
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
)
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if TYPE_CHECKING:
    from pathlib import Path

if is_matplotlib_available():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    from plotmux.backends.matplotlib.backend import (
        MatplotlibBackend,
        _draw_axes,
        _draw_primitive,
        draw_bars,
        draw_line,
        draw_points,
    )


@pytest.fixture
def backend() -> MatplotlibBackend:
    return MatplotlibBackend()


def _ax() -> Any:
    return Figure().subplots()


def _panel(*marks: Any, **kwargs: Any) -> PanelSpec:
    return PanelSpec(marks=marks, **kwargs)


LINE = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
RED = (1.0, 0.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)

#######################################
#     Tests for MatplotlibBackend     #
#######################################


@matplotlib_available
def test_backend_name(backend: MatplotlibBackend) -> None:
    assert backend.name == "matplotlib"


@matplotlib_available
def test_backend_capabilities_formats(backend: MatplotlibBackend) -> None:
    assert backend.capabilities().formats == frozenset({"png", "svg", "pdf", "jpg", "jpeg"})


@matplotlib_available
def test_backend_capabilities_grid_formats(backend: MatplotlibBackend) -> None:
    assert backend.capabilities().grid_formats == backend.capabilities().formats


@matplotlib_available
def test_backend_capabilities_legend_locations(backend: MatplotlibBackend) -> None:
    assert backend.capabilities().legend_locations == frozenset(
        {"top_left", "top_right", "bottom_left", "bottom_right", "top", "bottom", "left", "right"}
    )


@matplotlib_available
def test_backend_capabilities_markers(backend: MatplotlibBackend) -> None:
    assert backend.capabilities().markers == frozenset(
        {"circle", "square", "triangle", "diamond", "cross", "x"}
    )


@matplotlib_available
def test_backend_capabilities_name(backend: MatplotlibBackend) -> None:
    assert backend.capabilities().name == "matplotlib"


# --- render ---


@matplotlib_available
def test_backend_render_returns_a_figure(backend: MatplotlibBackend) -> None:
    assert isinstance(backend.render(_panel(LINE)), Figure)


@matplotlib_available
def test_backend_render_histogram_draws_the_bins(backend: MatplotlibBackend) -> None:
    native = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10)))
    assert len(native.axes[0].patches) == 10


@matplotlib_available
def test_backend_render_histogram_density_integrates_to_one(backend: MatplotlibBackend) -> None:
    native = backend.render(_panel(HistogramSpec(values=np.arange(101), bins=10, density=True)))
    assert sum(p.get_height() * p.get_width() for p in native.axes[0].patches) == pytest.approx(1.0)


@matplotlib_available
def test_backend_render_cdf_goes_from_zero_to_one(backend: MatplotlibBackend) -> None:
    native = backend.render(_panel(CdfSpec(values=np.arange(11.0))))
    y = native.axes[0].lines[0].get_ydata()
    assert (y[0], y[-1]) == (0.0, 1.0)


@matplotlib_available
def test_backend_render_layer_draws_every_mark(backend: MatplotlibBackend) -> None:
    native = backend.render(_panel(LINE, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert (len(native.axes[0].lines), len(native.axes[0].collections)) == (1, 1)


@matplotlib_available
def test_backend_render_slope_alone(backend: MatplotlibBackend) -> None:
    native = backend.render(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1))
    assert len(native.axes[0].lines) == 1


@matplotlib_available
def test_backend_render_slope_in_a_grid(backend: MatplotlibBackend) -> None:
    grid = GridSpec(panels=(_panel(SlopeSpec(gradient=2.0), xmin=0, xmax=1),))
    assert len(backend.render(grid).axes[0].lines) == 1


@matplotlib_available
def test_backend_render_grid_has_one_axes_per_panel(backend: MatplotlibBackend) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE), _panel(LINE)), ncols=2))
    assert len(native.axes) == 2


@matplotlib_available
def test_backend_render_grid_hides_the_trailing_axes(backend: MatplotlibBackend) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),) * 3, ncols=2))
    assert [ax.get_visible() for ax in native.axes] == [True, True, True, False]


@matplotlib_available
def test_backend_render_grid_title(backend: MatplotlibBackend) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),), title="t"))
    assert native._suptitle.get_text() == "t"


@matplotlib_available
def test_backend_render_grid_without_title(backend: MatplotlibBackend) -> None:
    assert backend.render(GridSpec(panels=(_panel(LINE),)))._suptitle is None


@matplotlib_available
def test_backend_render_styles_each_grid_panel(backend: MatplotlibBackend) -> None:
    grid = GridSpec(panels=(_panel(LINE, title="a"), _panel(LINE, title="b")), ncols=2)
    assert [ax.get_title() for ax in backend.render(grid).axes] == ["a", "b"]


@matplotlib_available
def test_backend_render_unsupported_legend_location_raises_before_drawing(
    backend: MatplotlibBackend,
) -> None:
    scene = AxesScene(primitives=(), legend=LegendStyle(location=cast("Any", "best")))
    with pytest.raises(UnsupportedSpecError, match="does not support legend_location='best'"):
        backend.capabilities().check(scene)


@matplotlib_available
def test_backend_render_every_marker_is_supported(backend: MatplotlibBackend) -> None:
    mark = ScatterSpec(x=np.arange(3), y=np.arange(3), marker="cross")
    assert len(backend.render(_panel(mark)).axes[0].collections) == 1


@matplotlib_available
def test_backend_render_does_not_register_with_pyplot(backend: MatplotlibBackend) -> None:
    # Regression test: rendering must not go through ``pyplot.subplots()``,
    # which registers the figure with pyplot's global figure manager and
    # keeps it alive (a leak) until ``plt.close()`` is called explicitly.
    before = set(plt.get_fignums())
    backend.render(_panel(LINE))
    assert set(plt.get_fignums()) == before


@matplotlib_available
def test_backend_render_does_not_change_the_spec(backend: MatplotlibBackend) -> None:
    spec = _panel(LINE)
    backend.render(spec)
    assert spec == _panel(LINE)


@matplotlib_available
def test_backend_render_is_deterministic(backend: MatplotlibBackend) -> None:
    first = backend.render(_panel(LINE)).axes[0].lines[0].get_color()
    assert backend.render(_panel(LINE)).axes[0].lines[0].get_color() == first


# --- draw ---


@matplotlib_available
def test_backend_draw_axes_scene(backend: MatplotlibBackend) -> None:
    assert len(backend.draw(AxesScene(primitives=())).axes) == 1


@matplotlib_available
def test_backend_draw_grid_scene(backend: MatplotlibBackend) -> None:
    scene = GridScene(panels=(AxesScene(primitives=()),) * 2, ncols=2)
    assert len(backend.draw(scene).axes) == 2


# --- save ---


@pytest.mark.parametrize("fmt", ["png", "svg", "pdf", "jpg", "jpeg"])
@matplotlib_available
def test_backend_save_supported_formats(
    backend: MatplotlibBackend, tmp_path: Path, fmt: str
) -> None:
    path = tmp_path / f"fig.{fmt}"
    backend.save(backend.render(_panel(LINE)), path, fmt)
    assert path.is_file()


@matplotlib_available
def test_backend_save_grid(backend: MatplotlibBackend, tmp_path: Path) -> None:
    path = tmp_path / "grid.png"
    backend.save(backend.render(GridSpec(panels=(_panel(LINE),))), path, "png")
    assert path.is_file()


# --- show ---


@matplotlib_available
def test_backend_show_non_interactive_warns(backend: MatplotlibBackend) -> None:
    # Regression test: ``Figure.show`` raised ``AttributeError`` on a figure
    # built without pyplot.
    native = backend.render(_panel(LINE))
    with pytest.warns(UserWarning, match="non-interactive"):
        backend.show(native)
    plt.close("all")


@matplotlib_available
def test_backend_show_keeps_the_figure_saveable(backend: MatplotlibBackend, tmp_path: Path) -> None:
    native = backend.render(_panel(LINE))
    with pytest.warns(UserWarning, match="non-interactive"):
        backend.show(native)
    backend.save(native, tmp_path / "out.png", "png")
    plt.close("all")
    assert (tmp_path / "out.png").exists()


# --- mimebundle ---


@matplotlib_available
def test_backend_mimebundle_keys(backend: MatplotlibBackend) -> None:
    assert list(cast("dict[str, Any]", backend.mimebundle(backend.render(_panel(LINE))))) == [
        "image/png"
    ]


@matplotlib_available
def test_backend_mimebundle_is_base64_png(backend: MatplotlibBackend) -> None:
    bundle = cast("dict[str, Any]", backend.mimebundle(backend.render(_panel(LINE))))
    assert base64.b64decode(bundle["image/png"]).startswith(b"\x89PNG\r\n\x1a\n")


@matplotlib_available
def test_backend_mimebundle_grid(backend: MatplotlibBackend) -> None:
    native = backend.render(GridSpec(panels=(_panel(LINE),)))
    assert list(cast("dict[str, Any]", backend.mimebundle(native))) == ["image/png"]


#################################
#     Tests for draw_bars       #
#################################


def _bars(**kwargs: Any) -> Bars:
    defaults: dict[str, Any] = {
        "x": np.array([1.0, 3.0]),
        "height": np.array([2.0, 4.0]),
        "base": np.array([0.0, 1.0]),
        "width": 0.5,
        "color": RED,
    }
    return Bars(**{**defaults, **kwargs})


@matplotlib_available
def test_draw_bars_geometry() -> None:
    ax = _ax()
    draw_bars(ax, _bars())
    assert [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in ax.patches] == [
        (0.75, 0.0, 0.5, 2.0),
        (2.75, 1.0, 0.5, 4.0),
    ]


@matplotlib_available
def test_draw_bars_array_width() -> None:
    ax = _ax()
    draw_bars(ax, _bars(width=np.array([2.0, 1.0])))
    assert [p.get_width() for p in ax.patches] == [2.0, 1.0]


@matplotlib_available
def test_draw_bars_color() -> None:
    ax = _ax()
    draw_bars(ax, _bars())
    assert ax.patches[0].get_facecolor() == RED


@matplotlib_available
def test_draw_bars_alpha() -> None:
    ax = _ax()
    draw_bars(ax, _bars(alpha=0.5))
    assert ax.patches[0].get_alpha() == 0.5


@matplotlib_available
def test_draw_bars_label() -> None:
    ax = _ax()
    draw_bars(ax, _bars(label="a"))
    assert ax.get_legend_handles_labels()[1] == ["a"]


@matplotlib_available
def test_draw_bars_without_label_has_no_legend_entry() -> None:
    ax = _ax()
    draw_bars(ax, _bars())
    assert ax.get_legend_handles_labels()[1] == []


@matplotlib_available
def test_draw_bars_categorical() -> None:
    ax = _ax()
    draw_bars(ax, _bars(x=np.array(["a", "b"])))
    assert [t.get_text() for t in ax.get_xticklabels()] == ["a", "b"]


@matplotlib_available
def test_draw_bars_does_not_change_the_primitive() -> None:
    bars = _bars()
    draw_bars(_ax(), bars)
    assert bars == _bars()


#################################
#     Tests for draw_line       #
#################################


def _line(**kwargs: Any) -> Line:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Line(**{**defaults, **kwargs})


@matplotlib_available
def test_draw_line_data() -> None:
    ax = _ax()
    draw_line(ax, _line())
    assert ax.lines[0].get_data()[1].tolist() == [2.0, 3.0]


@matplotlib_available
def test_draw_line_style() -> None:
    ax = _ax()
    draw_line(ax, _line(alpha=0.5, linewidth=3.0, linestyle="dashed"))
    line = ax.lines[0]
    assert (line.get_alpha(), line.get_linewidth(), line.get_linestyle()) == (0.5, 3.0, "--")


@matplotlib_available
def test_draw_line_color() -> None:
    ax = _ax()
    draw_line(ax, _line())
    assert ax.lines[0].get_color() == RED


@matplotlib_available
def test_draw_line_label() -> None:
    ax = _ax()
    draw_line(ax, _line(label="a"))
    assert ax.get_legend_handles_labels()[1] == ["a"]


@matplotlib_available
def test_draw_line_nan_is_a_gap() -> None:
    ax = _ax()
    draw_line(ax, _line(y=np.array([1.0, np.nan])))
    assert np.isnan(ax.lines[0].get_ydata()[1])


@matplotlib_available
def test_draw_line_infinite_is_drawn_with_axline() -> None:
    ax = _ax()
    draw_line(ax, _line(infinite=(2.0, 1.0)))
    assert type(ax.lines[0]).__name__ == "AxLine"


@matplotlib_available
def test_draw_line_infinite_keeps_the_slope() -> None:
    ax = _ax()
    draw_line(ax, _line(infinite=(2.0, 1.0)))
    assert ax.lines[0]._slope == 2.0


@matplotlib_available
def test_draw_line_infinite_keeps_the_intercept() -> None:
    ax = _ax()
    draw_line(ax, _line(infinite=(2.0, 1.0)))
    assert ax.lines[0]._xy1 == (0, 1.0)


@matplotlib_available
def test_draw_line_infinite_style() -> None:
    ax = _ax()
    draw_line(ax, _line(infinite=(2.0, 1.0), linewidth=3.0, label="a"))
    assert (ax.lines[0].get_linewidth(), ax.get_legend_handles_labels()[1]) == (3.0, ["a"])


#################################
#     Tests for draw_points     #
#################################


def _points(**kwargs: Any) -> Points:
    defaults: dict[str, Any] = {"x": np.array([0.0, 1.0]), "y": np.array([2.0, 3.0]), "color": RED}
    return Points(**{**defaults, **kwargs})


@matplotlib_available
def test_draw_points_offsets() -> None:
    ax = _ax()
    draw_points(ax, _points())
    assert ax.collections[0].get_offsets().tolist() == [[0.0, 2.0], [1.0, 3.0]]


@matplotlib_available
def test_draw_points_color() -> None:
    ax = _ax()
    draw_points(ax, _points())
    assert ax.collections[0].get_facecolor().tolist() == [list(RED)]


@matplotlib_available
def test_draw_points_size() -> None:
    ax = _ax()
    draw_points(ax, _points(size=30.0))
    assert ax.collections[0].get_sizes().tolist() == [30.0]


@matplotlib_available
def test_draw_points_alpha() -> None:
    ax = _ax()
    draw_points(ax, _points(alpha=0.5))
    assert ax.collections[0].get_alpha() == 0.5


@matplotlib_available
def test_draw_points_label() -> None:
    ax = _ax()
    draw_points(ax, _points(label="a"))
    assert ax.get_legend_handles_labels()[1] == ["a"]


@matplotlib_available
def test_draw_points_marker() -> None:
    ax = _ax()
    draw_points(ax, _points(marker="square"))
    assert ax.collections[0].get_paths()[0].vertices.shape[0] == 5


@matplotlib_available
def test_draw_points_edgecolor() -> None:
    ax = _ax()
    draw_points(ax, _points(edgecolor=BLUE))
    assert ax.collections[0].get_edgecolor().tolist() == [list(BLUE)]


@matplotlib_available
def test_draw_points_without_edgecolor_uses_the_color() -> None:
    ax = _ax()
    draw_points(ax, _points())
    assert ax.collections[0].get_edgecolor().tolist() == [list(RED)]


@matplotlib_available
def test_draw_points_hollow_has_no_fill() -> None:
    ax = _ax()
    draw_points(ax, _points(fill=False))
    assert ax.collections[0].get_facecolor().shape == (0, 4)


@matplotlib_available
def test_draw_points_hollow_outline_is_the_color() -> None:
    ax = _ax()
    draw_points(ax, _points(fill=False))
    assert ax.collections[0].get_edgecolor().tolist() == [list(RED)]


@matplotlib_available
def test_draw_points_hollow_outline_is_the_edgecolor() -> None:
    ax = _ax()
    draw_points(ax, _points(fill=False, edgecolor=BLUE))
    assert ax.collections[0].get_edgecolor().tolist() == [list(BLUE)]


@matplotlib_available
def test_draw_points_fill_true_is_filled() -> None:
    ax = _ax()
    draw_points(ax, _points(fill=True))
    assert ax.collections[0].get_facecolor().tolist() == [list(RED)]


#######################################
#     Tests for _draw_primitive       #
#######################################


@matplotlib_available
def test_draw_primitive_bars() -> None:
    ax = _ax()
    _draw_primitive(ax, _bars())
    assert len(ax.patches) == 2


@matplotlib_available
def test_draw_primitive_line() -> None:
    ax = _ax()
    _draw_primitive(ax, _line())
    assert len(ax.lines) == 1


@matplotlib_available
def test_draw_primitive_points() -> None:
    ax = _ax()
    _draw_primitive(ax, _points())
    assert len(ax.collections) == 1


##################################
#     Tests for _draw_axes       #
##################################


@matplotlib_available
def test_draw_axes_draws_in_order() -> None:
    ax = _ax()
    _draw_axes(ax, AxesScene(primitives=(_line(), _points())))
    assert (len(ax.lines), len(ax.collections)) == (1, 1)


@matplotlib_available
def test_draw_axes_applies_the_style() -> None:
    ax = _ax()
    _draw_axes(ax, AxesScene(primitives=(), title="t"))
    assert ax.get_title() == "t"


@matplotlib_available
def test_draw_axes_legend_lists_the_labels_in_order() -> None:
    ax = _ax()
    scene = AxesScene(
        primitives=(_line(label="a"), _points(label="b")), legend=LegendStyle(title="l")
    )
    _draw_axes(ax, scene)
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["a", "b"]
