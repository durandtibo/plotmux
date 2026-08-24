from __future__ import annotations

import numpy as np
import pytest

from plotmux.core.specs import HistogramSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.backend import XyBackend


@pytest.fixture
def backend() -> object:
    return XyBackend()


@xy_available
def test_xy_backend_name(backend) -> None:  # noqa: ANN001
    assert backend.name == "xy"


@xy_available
def test_xy_backend_render_histogram(backend) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_histogram_density(backend) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Chart)


@xy_available
def test_xy_backend_render_unsupported_spec(backend) -> None:  # noqa: ANN001
    with pytest.raises(NotImplementedError, match="No xy renderer registered"):
        backend.render(object())


@xy_available
def test_xy_backend_save_unsupported_format(backend, tmp_path) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.txt", "txt")


@xy_available
def test_xy_backend_save_png(backend, tmp_path) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / "fig.png"
    backend.save(native, path, "png")
    assert path.is_file()


@xy_available
def test_xy_backend_save_html(backend, tmp_path) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / "fig.html"
    backend.save(native, path, "html")
    assert path.is_file()
