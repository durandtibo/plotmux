from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from plotmux.backends.base import Backend, make_renderer

if TYPE_CHECKING:
    from pathlib import Path


class FakeBackend(Backend):
    name = "fake"
    supported_formats = frozenset({"png"})

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


def test_backend_supported_formats() -> None:
    backend = FakeBackend()
    assert backend.supported_formats == frozenset({"png"})


####################################
#     Tests for make_renderer     #
####################################


def test_make_renderer_draws_then_styles() -> None:
    calls = []

    def chart_render(spec: Any, **kwargs: Any) -> str:
        calls.append(("draw", spec, kwargs))
        return "native"

    def style(native: str, spec: Any) -> str:
        calls.append(("style", native, spec))
        return f"{native}-styled"

    render = make_renderer(chart_render, style)
    result = render("spec", alpha=0.5)

    assert result == "native-styled"
    assert calls == [("draw", "spec", {"alpha": 0.5}), ("style", "native", "spec")]
