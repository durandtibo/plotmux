from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from plotmux.backends.base import Backend
from plotmux.backends.registry import _REGISTRY, register_backend
from plotmux.export import save
from plotmux.figure import Figure
from plotmux.specs import HistogramSpec

if TYPE_CHECKING:
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
def _restore_registry() -> Any:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def test_save_infers_format_from_suffix(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    fig = Figure(spec=HistogramSpec(values=[1, 2, 3]), backend_name="fake", native="native-object")
    save(fig, tmp_path / "out.svg")
    assert fake_backend.saved == [("native-object", tmp_path / "out.svg", "svg")]


def test_save_no_suffix_raises(tmp_path: Path) -> None:
    fig = Figure(spec=HistogramSpec(values=[1, 2, 3]), backend_name="fake", native="native-object")
    with pytest.raises(ValueError, match="Cannot infer the export format"):
        save(fig, tmp_path / "out")


def test_save_creates_missing_parent_directories(tmp_path: Path) -> None:
    fake_backend = FakeBackend()
    register_backend(fake_backend)
    fig = Figure(spec=HistogramSpec(values=[1, 2, 3]), backend_name="fake", native="native-object")
    path = tmp_path / "a" / "b" / "out.png"
    assert not path.parent.exists()
    save(fig, path)
    assert path.parent.is_dir()
    assert fake_backend.saved == [("native-object", path, "png")]
