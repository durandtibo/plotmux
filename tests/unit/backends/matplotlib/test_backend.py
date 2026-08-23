from __future__ import annotations

import numpy as np
import pytest

from plotmux.core.specs import HistogramSpec
from plotmux.testing.fixtures import matplotlib_available


@pytest.fixture
def backend() -> object:
    from plotmux.backends.matplotlib.backend import MatplotlibBackend

    return MatplotlibBackend()


@matplotlib_available
def test_matplotlib_backend_name(backend) -> None:  # noqa: ANN001
    assert backend.name == "matplotlib"


@matplotlib_available
def test_matplotlib_backend_render_histogram(backend) -> None:  # noqa: ANN001
    from matplotlib.figure import Figure

    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_histogram_density(backend) -> None:  # noqa: ANN001
    from matplotlib.figure import Figure

    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    heights = [patch.get_height() for patch in ax.patches]
    # The area under the histogram integrates to 1 when density=True.
    assert sum(heights) * (100 / 10) == pytest.approx(1.0)


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
