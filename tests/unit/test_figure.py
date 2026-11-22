from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import numpy as np
import pytest

from plotmux.backends.registry import _REGISTRY, register_backend
from plotmux.figure import Figure
from plotmux.specs import GridSpec, HistogramSpec, PanelSpec
from tests.fakes import FakeBackend

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class RecordingBackend(FakeBackend):
    formats = frozenset({"png", "svg"})
    grid_formats = frozenset({"png"})

    def __init__(self) -> None:
        super().__init__()
        self.shown: list[Any] = []

    def show(self, native: Any) -> None:
        self.shown.append(native)

    def mimebundle(self, native: Any) -> dict[str, Any] | None:
        return {"text/html": f"<b>{native}</b>", "image/png": "png"}


class BareBackend(FakeBackend):
    name = "bare"


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
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.to_native() == "native-object"


##############################
#     Tests for Figure.show     #
##############################


def test_figure_show_delegates_to_backend() -> None:
    backend = RecordingBackend()
    register_backend(backend)
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    Figure(spec=spec, backend_name="fake", native="native-object").show()
    assert backend.shown == ["native-object"]


def test_figure_show_unsupported_backend() -> None:
    register_backend(BareBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="bare", native="native-object")
    with pytest.raises(NotImplementedError, match="The bare backend does not support 'show'"):
        fig.show()


##############################
#     Tests for Figure.save     #
##############################


def test_figure_save(tmp_path: Path) -> None:
    fake_backend = RecordingBackend()
    register_backend(fake_backend)
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(tmp_path / "out.png")
    assert fake_backend.saved == [("native-object", tmp_path / "out.png", "png")]


def test_figure_save_accepts_str_path(tmp_path: Path) -> None:
    fake_backend = RecordingBackend()
    register_backend(fake_backend)
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    fig.save(str(tmp_path / "out.svg"))
    assert fake_backend.saved == [("native-object", tmp_path / "out.svg", "svg")]


##########################################
#     Tests for Figure.supported_formats     #
##########################################


def test_figure_supported_formats() -> None:
    register_backend(RecordingBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig.supported_formats == frozenset({"png", "svg"})


def test_figure_supported_formats_of_a_grid() -> None:
    register_backend(RecordingBackend())
    panel = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=GridSpec(panels=(panel,)), backend_name="fake", native="native-object")
    assert fig.supported_formats == frozenset({"png"})


#######################################
#     Tests for Figure rich display     #
#######################################


def test_figure_repr_mimebundle_delegates_to_backend() -> None:
    register_backend(RecordingBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_() == {"text/html": "<b>native-object</b>", "image/png": "png"}


def test_figure_repr_mimebundle_include() -> None:
    register_backend(RecordingBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(include={"image/png"}) == {"image/png": "png"}


def test_figure_repr_mimebundle_exclude() -> None:
    register_backend(RecordingBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(exclude={"image/png"}) == {"text/html": "<b>native-object</b>"}


def test_figure_repr_mimebundle_include_and_exclude() -> None:
    register_backend(RecordingBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native="native-object")
    assert fig._repr_mimebundle_(include={"image/png", "text/html"}, exclude={"image/png"}) == {
        "text/html": "<b>native-object</b>"
    }


def test_figure_repr_mimebundle_none_without_representation() -> None:
    register_backend(BareBackend())
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="bare", native=object())
    assert fig._repr_mimebundle_() is None


def test_figure_does_not_forward_unknown_attributes_to_native() -> None:
    spec = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=spec, backend_name="fake", native=Mock())
    assert not hasattr(fig, "_repr_html_")
