from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotmux.backends.base import Backend

if TYPE_CHECKING:
    from pathlib import Path


class FakeBackend(Backend):
    name = "fake"

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        del native, path, fmt


def test_backend_name() -> None:
    backend = FakeBackend()
    assert backend.name == "fake"


def test_backend_render() -> None:
    backend = FakeBackend()
    assert backend.render("spec") == "spec"


def test_backend_save() -> None:
    backend = FakeBackend()
    # Should not raise.
    backend.save("native", "path", "png")
