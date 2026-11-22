from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.backends.base import Backend, BackendCapabilities
from plotmux.exceptions import UnsupportedFormatError, UnsupportedSpecError
from plotmux.primitives import Line, Points
from plotmux.scene import AxesScene, GridScene, LegendStyle, build_scene
from plotmux.specs import GridSpec, LineSpec, PanelSpec, ScatterSpec
from tests.fakes import FakeBackend

CAPS = BackendCapabilities(
    name="demo",
    formats=frozenset({"png", "svg"}),
    grid_formats=frozenset({"png"}),
    legend_locations=frozenset({"top", "bottom"}),
    markers=frozenset({"circle", "square"}),
)
LINE = LineSpec(x=np.arange(3), y=np.arange(3), label="a")


def _points(marker: str | None) -> Points:
    return Points(x=np.arange(2.0), y=np.arange(2.0), marker=marker)


def _scene(location: str | None = None, *primitives: Any) -> AxesScene:
    legend = None if location is None else LegendStyle(location=cast("Any", location))
    return AxesScene(primitives=primitives, legend=legend)


#####################################
#     Tests for BackendCapabilities #
#####################################


def test_capabilities_check_accepts_a_supported_scene() -> None:
    CAPS.check(_scene("top", _points("square")))


def test_capabilities_check_accepts_no_legend_and_no_marker() -> None:
    CAPS.check(_scene(None, _points(None), Line(x=np.arange(2.0), y=np.arange(2.0))))


def test_capabilities_check_legend_without_location() -> None:
    CAPS.check(AxesScene(primitives=(), legend=LegendStyle(title="t")))


def test_capabilities_check_unsupported_legend_location_raises() -> None:
    with pytest.raises(
        UnsupportedSpecError,
        match=r"The demo backend does not support legend_location='left': "
        r"supported values are \['bottom', 'top'\]",
    ):
        CAPS.check(_scene("left"))


def test_capabilities_check_unsupported_marker_raises() -> None:
    with pytest.raises(
        UnsupportedSpecError,
        match=r"The demo backend does not support marker='x': "
        r"supported values are \['circle', 'square'\]",
    ):
        CAPS.check(_scene(None, _points("x")))


def test_capabilities_check_checks_every_panel_of_a_grid() -> None:
    grid = GridScene(panels=(_scene("top"), _scene("left")))
    with pytest.raises(UnsupportedSpecError, match="legend_location='left'"):
        CAPS.check(grid)


def test_capabilities_check_accepts_a_supported_grid() -> None:
    CAPS.check(GridScene(panels=(_scene("top"), _scene("bottom"))))


@pytest.mark.parametrize("fmt", ["png", "svg"])
def test_capabilities_check_format_supported(fmt: str) -> None:
    CAPS.check_format(fmt)


def test_capabilities_check_format_unsupported_raises() -> None:
    with pytest.raises(
        UnsupportedFormatError,
        match=r"The demo backend does not support exporting a figure to 'pdf': "
        r"supported formats are \['png', 'svg'\]",
    ):
        CAPS.check_format("pdf")


def test_capabilities_check_format_grid_supported() -> None:
    CAPS.check_format("png", grid=True)


def test_capabilities_check_format_grid_unsupported_raises() -> None:
    with pytest.raises(
        UnsupportedFormatError,
        match=r"The demo backend does not support exporting a grid to 'svg': "
        r"supported formats are \['png'\]",
    ):
        CAPS.check_format("svg", grid=True)


def test_capabilities_are_immutable() -> None:
    with pytest.raises(AttributeError):
        cast("Any", CAPS).name = "other"


##############################
#     Tests for Backend      #
##############################


def test_backend_name() -> None:
    assert FakeBackend().name == "fake"


def test_backend_is_abstract() -> None:
    with pytest.raises(TypeError, match="abstract"):
        cast("Any", Backend)()


def test_backend_without_draw_is_abstract() -> None:
    class NoDraw(Backend):
        name = "nodraw"

        def capabilities(self) -> BackendCapabilities:
            return CAPS

        def save(self, native: Any, path: Any, fmt: str) -> None:
            del native, path, fmt

    with pytest.raises(TypeError, match="abstract"):
        cast("Any", NoDraw)()


def test_backend_render_draws_the_scene_of_the_spec() -> None:
    spec = PanelSpec(marks=(LINE,))
    assert FakeBackend().render(spec) == build_scene(spec)


def test_backend_render_grid() -> None:
    spec = GridSpec(panels=(PanelSpec(marks=(LINE,)),))
    assert FakeBackend().render(spec) == build_scene(spec)


def test_backend_render_checks_before_drawing() -> None:
    class CountingBackend(FakeBackend):
        drawn = 0

        def draw(self, scene: Any) -> Any:
            type(self).drawn += 1
            return scene

    spec = PanelSpec(marks=(LINE,), legend_location="left")
    with pytest.raises(UnsupportedSpecError, match="legend_location='left'"):
        CountingBackend().render(spec)
    assert CountingBackend.drawn == 0


def test_backend_render_unsupported_marker_raises() -> None:
    spec = PanelSpec(marks=(ScatterSpec(x=np.arange(2), y=np.arange(2), marker="x"),))
    with pytest.raises(UnsupportedSpecError, match="marker='x'"):
        FakeBackend().render(spec)


def test_backend_render_does_not_take_keyword_arguments() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        cast("Any", FakeBackend()).render(PanelSpec(marks=(LINE,)), linewidth=2)


def test_backend_save() -> None:
    backend = FakeBackend()
    backend.save("native", cast("Any", "path"), "png")
    assert backend.saved == [("native", "path", "png")]


##################################
#     Tests for Backend.show     #
##################################


def test_backend_show_raises_by_default() -> None:
    with pytest.raises(NotImplementedError, match="The fake backend does not support 'show'"):
        FakeBackend().show("native")


########################################
#     Tests for Backend.mimebundle     #
########################################


class NativeWithMimebundle:
    def _repr_mimebundle_(self) -> dict[str, Any]:
        return {"text/plain": "bundle"}


class NativeWithReprs:
    def _repr_html_(self) -> str:
        return "<b>html</b>"

    def _repr_png_(self) -> bytes:
        return b"png"

    def _repr_svg_(self) -> None:
        return None


def test_backend_mimebundle_uses_native_mimebundle() -> None:
    assert FakeBackend().mimebundle(NativeWithMimebundle()) == {"text/plain": "bundle"}


def test_backend_mimebundle_uses_native_repr_methods() -> None:
    assert FakeBackend().mimebundle(NativeWithReprs()) == {
        "text/html": "<b>html</b>",
        "image/png": b"png",
    }


def test_backend_mimebundle_none_without_representation() -> None:
    assert FakeBackend().mimebundle(object()) is None
