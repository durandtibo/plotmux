from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import numpy as np
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
        self.shown: list[Any] = []

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        self.saved.append((native, path, fmt))

    def show(self, native: Any) -> None:
        self.shown.append(native)

    def mimebundle(self, native: Any) -> dict[str, Any] | None:
        return {"text/html": f"<b>{native}</b>", "image/png": "png"}


class BareBackend(Backend):
    name = "bare"
    supported_formats = frozenset({"png"})

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        del native, path, fmt


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
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.to_native() == "native-object"


##############################
#     Tests for Figure.show     #
##############################


def test_figure_show_delegates_to_backend() -> None:
    backend = FakeBackend()
    register_backend(backend)
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    Figure(spec=spec, backend_name="fake", native="native-object").show()
    assert backend.shown == ["native-object"]


def test_figure_show_unsupported_backend() -> None:
    register_backend(BareBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="bare", native="native-object")
    with pytest.raises(NotImplementedError, match="The bare backend does not support 'show'"):
        fig.show()


##############################
#     Tests for Figure.save     #
##############################


def test_figure_save(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(tmp_path / "out.png")
    assert fake_backend.saved == [("native-object", tmp_path / "out.png", "png")]


def test_figure_save_accepts_str_path(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(str(tmp_path / "out.svg"))
    assert fake_backend.saved == [("native-object", tmp_path / "out.svg", "svg")]


##########################################
#     Tests for Figure.supported_formats     #
##########################################


def test_figure_supported_formats() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.supported_formats == frozenset({"png", "svg"})


#######################################
#     Tests for Figure rich display     #
#######################################


def test_figure_repr_mimebundle_delegates_to_backend() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_() == {"text/html": "<b>native-object</b>", "image/png": "png"}


def test_figure_repr_mimebundle_include() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(include={"image/png"}) == {"image/png": "png"}


def test_figure_repr_mimebundle_exclude() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(exclude={"image/png"}) == {"text/html": "<b>native-object</b>"}


def test_figure_repr_mimebundle_include_and_exclude() -> None:
    register_backend(FakeBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(include={"image/png", "text/html"}, exclude={"image/png"}) == {
        "text/html": "<b>native-object</b>"
    }


def test_figure_repr_mimebundle_none_without_representation() -> None:
    register_backend(BareBackend())
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="bare", native=object())
    assert fig._repr_mimebundle_() is None


def test_figure_does_not_forward_unknown_attributes_to_native() -> None:
    spec = HistogramSpec(values=np.array([1, 2, 3]))
    fig = Figure(spec=spec, backend_name="fake", native=Mock())
    assert not hasattr(fig, "_repr_html_")
