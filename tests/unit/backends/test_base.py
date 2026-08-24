from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

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


##############################
#     Tests for Backend     #
##############################


def test_backend_name() -> None:
    backend = FakeBackend()
    assert backend.name == "fake"


def test_backend_render() -> None:
    backend = FakeBackend()
    assert backend.render("spec") == "spec"


def test_backend_render_forwards_kwargs() -> None:
    class KwargsBackend(Backend):
        name = "kwargs"

        def render(self, spec: Any, **kwargs: Any) -> Any:
            del spec
            return kwargs

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    backend = KwargsBackend()
    assert backend.render("spec", alpha=0.5) == {"alpha": 0.5}


def test_backend_save() -> None:
    backend = FakeBackend()
    # Should not raise.
    backend.save("native", "path", "png")


def test_backend_is_abstract() -> None:
    class IncompleteBackend(Backend):
        name = "incomplete"

    with pytest.raises(TypeError, match="abstract"):
        IncompleteBackend()  # type: ignore[abstract]
