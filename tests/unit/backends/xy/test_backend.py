from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if TYPE_CHECKING:
    from pathlib import Path

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.backend import XyBackend


@pytest.fixture
def backend() -> XyBackend:
    return XyBackend()


##############################
#     Tests for XyBackend     #
##############################


@xy_available
def test_xy_backend_name(backend: XyBackend) -> None:
    assert backend.name == "xy"


# --- render ---


@xy_available
def test_xy_backend_render_histogram(backend: XyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_histogram_density(backend: XyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_line(backend: XyBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_scatter(backend: XyBackend) -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_layer(backend: XyBackend) -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, Chart)
    assert len(native.children) == 2 + 2  # 2 marks + x_axis + y_axis


@xy_available
def test_xy_backend_render_applies_common_style(backend: XyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    native = backend.render(spec)
    assert native.title == "my-title"


@xy_available
def test_xy_backend_render_unsupported_spec(backend: XyBackend) -> None:
    with pytest.raises(NotImplementedError, match="No xy renderer registered"):
        backend.render(object())


# --- save ---


@xy_available
def test_xy_backend_save_unsupported_format(backend: XyBackend, tmp_path: Path) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.txt", "txt")


@pytest.mark.parametrize("fmt", ["png", "svg", "html"])
@xy_available
def test_xy_backend_save_supported_formats(backend: XyBackend, tmp_path: Path, fmt: str) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / f"fig.{fmt}"
    backend.save(native, path, fmt)
    assert path.is_file()
