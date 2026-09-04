from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

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


def test_backend_capabilities_default_caveats() -> None:
    class RenderersBackend(Backend):
        name = "renderers"
        _RENDERERS: ClassVar[Any] = {int: str, float: str}

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    caps = RenderersBackend.capabilities()
    assert caps.backend_name == "renderers"
    assert caps.spec_types == frozenset({int, float})
    assert caps.caveats == ()


def test_backend_capabilities_with_caveats() -> None:
    class CaveatBackend(Backend):
        name = "caveat"
        _RENDERERS: ClassVar[Any] = {int: str}
        _CAVEATS: ClassVar[Any] = (
            "int is only supported nested inside a LayerSpec, not standalone.",
        )

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    caps = CaveatBackend.capabilities()
    assert caps.spec_types == frozenset({int})
    assert caps.caveats == ("int is only supported nested inside a LayerSpec, not standalone.",)


def test_backend_capabilities_is_instance_method_too() -> None:
    class RenderersBackend(Backend):
        name = "renderers"
        _RENDERERS: ClassVar[Any] = {int: str}

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    backend = RenderersBackend()
    assert backend.capabilities() == RenderersBackend.capabilities()


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
