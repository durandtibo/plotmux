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


##################################
#     Tests for Figure._backend     #
##################################


def test_figure_backend_returns_registered_backend() -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._backend() is fake_backend


def test_figure_backend_unknown_raises() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    fig = Figure(spec=spec, backend_name="does-not-exist", native="native-object")
    with pytest.raises(RuntimeError, match="No backend registered"):
        fig._backend()


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
