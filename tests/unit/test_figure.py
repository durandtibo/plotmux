from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest

from plotmux.backends.base import Backend
from plotmux.backends.registry import _REGISTRY, register_backend
from plotmux.figure import Figure
from plotmux.specs import HistogramSpec

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class FakeBackend(Backend):
    name = "fake"
    supported_formats = frozenset({"png", "svg"})

    def __init__(self) -> None:
        self.saved: list[tuple[Any, Path, str]] = []

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        self.saved.append((native, path, fmt))


@pytest.fixture(autouse=True)
def _restore_registry() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


##################################
#     Tests for Figure.to_native     #
##################################


def test_figure_to_native() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.to_native() == "native-object"


##############################
#     Tests for Figure.show     #
##############################


def test_figure_show_delegates_to_native() -> None:
    native = Mock()
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=native)
    fig.show()
    native.show.assert_called_once_with()


def test_figure_show_unsupported_native() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=object())
    with pytest.raises(NotImplementedError, match="does not support 'show'"):
        fig.show()


def test_figure_show_none_native() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=None)
    with pytest.raises(NotImplementedError, match="does not support 'show'"):
        fig.show()


##############################
#     Tests for Figure.save     #
##############################


def test_figure_save(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(tmp_path / "out.png")
    assert fake_backend.saved == [("native-object", tmp_path / "out.png", "png")]


def test_figure_save_accepts_str_path(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(str(tmp_path / "out.svg"))
    assert fake_backend.saved == [("native-object", tmp_path / "out.svg", "svg")]


##########################################
#     Tests for Figure.supported_formats     #
##########################################


def test_figure_supported_formats() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.supported_formats == frozenset({"png", "svg"})


##########################################
#     Tests for Figure rich display     #
##########################################


def test_figure_repr_html_forwards_to_native() -> None:
    native = Mock()
    native._repr_html_.return_value = "<div>native</div>"
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=native)
    assert fig._repr_html_() == "<div>native</div>"


def test_figure_repr_mimebundle_forwards_to_native() -> None:
    native = Mock()
    native._repr_mimebundle_.return_value = ({"text/plain": "x"}, {})
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=native)
    assert fig._repr_mimebundle_() == ({"text/plain": "x"}, {})


def test_figure_repr_svg_forwards_to_native() -> None:
    native = Mock()
    native._repr_svg_.return_value = "<svg></svg>"
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=native)
    assert fig._repr_svg_() == "<svg></svg>"


def test_figure_repr_html_missing_on_native_raises() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=object())
    with pytest.raises(AttributeError):
        fig._repr_html_()


def test_figure_repr_png_forwards_to_native_repr_png() -> None:
    native = Mock()
    native._repr_png_.return_value = b"native-png-bytes"
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=native)
    assert fig._repr_png_() == b"native-png-bytes"


def test_figure_repr_png_falls_back_to_canvas_print_png() -> None:
    class FakeCanvas:
        def print_png(self, buffer: Any) -> None:
            buffer.write(b"canvas-png-bytes")

    class FakeNative:
        canvas = FakeCanvas()

    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=FakeNative())
    assert fig._repr_png_() == b"canvas-png-bytes"


def test_figure_repr_png_none_when_unsupported() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=object())
    assert fig._repr_png_() is None


def test_figure_getattr_unknown_attribute_raises() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native=object())
    with pytest.raises(AttributeError, match="no attribute 'not_a_real_method'"):
        fig.not_a_real_method()
