from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from plotmux.backends.registry import _REGISTRY, register_backend
from plotmux.exceptions import UnsupportedFormatError
from plotmux.export import save
from plotmux.figure import Figure
from plotmux.specs import GridSpec, HistogramSpec, PanelSpec
from tests.fakes import FakeBackend

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class FakeBackendWithFormats(FakeBackend):
    formats = frozenset({"svg"})


@pytest.fixture(autouse=True)
def _restore_registry() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def _make_figure() -> Figure:
    return Figure(
        spec=PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),)),
        backend_name="fake",
        native="native-object",
    )


##########################
#     Tests for save     #
##########################


def test_save_infers_format_from_suffix(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    save(_make_figure(), tmp_path / "out.svg")
    assert fake_backend.saved == [("native-object", tmp_path / "out.svg", "svg")]


@pytest.mark.parametrize(
    ("filename", "expected_fmt"),
    [
        pytest.param("out.png", "png", id="png"),
        pytest.param("out.PNG", "png", id="uppercase_suffix_is_lowercased"),
        pytest.param("out.tar.gz", "gz", id="last_suffix_of_multi_dot_name"),
    ],
)
def test_save_infers_format_variants(tmp_path: Path, filename: str, expected_fmt: str) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    save(_make_figure(), tmp_path / filename)
    assert fake_backend.saved == [("native-object", tmp_path / filename, expected_fmt)]


def test_save_no_suffix_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Cannot infer the export format"):
        save(_make_figure(), tmp_path / "out")


def test_save_unsupported_format_raises_before_creating_parent_dir(tmp_path: Path) -> None:
    register_backend(FakeBackendWithFormats())
    fig = Figure(
        spec=PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),)),
        backend_name="fake",
        native="native-object",
    )
    target = tmp_path / "missing" / "out.png"
    with pytest.raises(
        UnsupportedFormatError, match=r"does not support exporting a figure to 'png'"
    ):
        save(fig, target)
    # The parent directory must not be created as a side effect of a
    # failed, unsupported-format save.
    assert not target.parent.exists()


def test_save_unknown_backend_raises(tmp_path: Path) -> None:
    fig = Figure(
        spec=PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),)),
        backend_name="does-not-exist",
        native=None,
    )
    with pytest.raises(RuntimeError, match="No backend registered"):
        save(fig, tmp_path / "out.png")


def test_save_creates_missing_parent_directories(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    path = tmp_path / "a" / "b" / "out.png"
    assert not path.parent.exists()
    save(_make_figure(), path)
    assert path.parent.is_dir()
    assert fake_backend.saved == [("native-object", path, "png")]


def test_save_existing_parent_directory(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    save(_make_figure(), tmp_path / "out.png")
    assert fake_backend.saved == [("native-object", tmp_path / "out.png", "png")]


def test_save_grid_unsupported_format_raises_before_creating_parent_dir(tmp_path: Path) -> None:
    register_backend(FakeBackend())
    panel = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=GridSpec(panels=(panel,)), backend_name="fake", native="native-object")
    target = tmp_path / "missing" / "out.svg"
    with pytest.raises(UnsupportedFormatError, match=r"does not support exporting a grid to 'svg'"):
        save(fig, target)
    assert not target.parent.exists()


def test_save_grid_supported_format(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    panel = PanelSpec(marks=(HistogramSpec(values=np.array([1, 2, 3])),))
    fig = Figure(spec=GridSpec(panels=(panel,)), backend_name="fake", native="native-object")
    save(fig, tmp_path / "out.png")
    assert fake_backend.saved == [("native-object", tmp_path / "out.png", "png")]
