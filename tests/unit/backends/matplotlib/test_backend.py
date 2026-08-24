from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    from matplotlib.figure import Figure

    from plotmux.backends.matplotlib.backend import MatplotlibBackend


@pytest.fixture
def backend() -> object:
    return MatplotlibBackend()


@matplotlib_available
def test_matplotlib_backend_name(backend) -> None:  # noqa: ANN001
    assert backend.name == "matplotlib"


@matplotlib_available
def test_matplotlib_backend_render_histogram(backend) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_histogram_density(backend) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    heights = [patch.get_height() for patch in ax.patches]
    # The area under the histogram integrates to 1 when density=True.
    assert sum(heights) * (100 / 10) == pytest.approx(1.0)


@matplotlib_available
def test_matplotlib_backend_render_histogram_label(backend) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    assert ax.get_legend() is not None


@matplotlib_available
def test_matplotlib_backend_render_line(backend) -> None:  # noqa: ANN001
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_scatter(backend) -> None:  # noqa: ANN001
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_layer(backend) -> None:  # noqa: ANN001
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1


@matplotlib_available
def test_matplotlib_backend_render_unsupported_spec(backend) -> None:  # noqa: ANN001
    with pytest.raises(NotImplementedError, match="No matplotlib renderer registered"):
        backend.render(object())


@matplotlib_available
def test_matplotlib_backend_save_unsupported_format(backend, tmp_path) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.txt", "txt")


@matplotlib_available
def test_matplotlib_backend_save_png(backend, tmp_path) -> None:  # noqa: ANN001
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / "fig.png"
    backend.save(native, path, "png")
    assert path.is_file()
