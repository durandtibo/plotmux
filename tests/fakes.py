r"""Contain the test doubles shared by the tests."""

from __future__ import annotations

__all__ = ["FakeBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

from plotmux.backends.base import Backend, BackendCapabilities

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.scene import AxesScene, GridScene


class FakeBackend(Backend):
    r"""Implement a backend that needs no plotting library.

    ``draw`` returns the scene itself, and ``save`` records its
    arguments in ``saved``.
    """

    name: ClassVar[str] = "fake"
    formats: ClassVar[frozenset[str]] = frozenset({"png", "svg", "gz"})
    grid_formats: ClassVar[frozenset[str]] = frozenset({"png"})

    def __init__(self) -> None:
        self.saved: list[tuple[Any, Path, str]] = []

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            formats=self.formats,
            grid_formats=self.grid_formats,
            legend_locations=frozenset({"top", "bottom"}),
            markers=frozenset({"circle"}),
        )

    def draw(self, scene: AxesScene | GridScene) -> Any:
        return scene

    def save(self, native: Any, path: Path, fmt: str) -> None:
        self.saved.append((native, path, fmt))
