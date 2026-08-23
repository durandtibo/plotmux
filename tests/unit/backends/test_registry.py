from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Iterator

from plotmux.backends.base import Backend
from plotmux.backends.registry import _REGISTRY, get_backend, register_backend


class FakeBackend(Backend):
    name = "fake"

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        pass


@pytest.fixture(autouse=True)
def _restore_registry() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def test_register_and_get_backend() -> None:
    register_backend(FakeBackend())
    assert isinstance(get_backend("fake"), FakeBackend)


def test_register_backend_replaces_existing() -> None:
    register_backend(FakeBackend())
    second = FakeBackend()
    register_backend(second)
    assert get_backend("fake") is second


def test_get_backend_missing() -> None:
    with pytest.raises(RuntimeError, match="No backend registered under the name 'missing'"):
        get_backend("missing")
