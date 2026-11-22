from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, cast

import numpy as np
import pytest

from plotmux.specs import (
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if TYPE_CHECKING:
    from pathlib import Path

if is_matplotlib_available():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    from plotmux.backends.matplotlib.backend import MatplotlibBackend


@pytest.fixture
def backend() -> MatplotlibBackend:
    return MatplotlibBackend()


########################################
#     Tests for MatplotlibBackend     #
########################################


@matplotlib_available
def test_matplotlib_backend_name(backend: MatplotlibBackend) -> None:
    assert backend.name == "matplotlib"


@matplotlib_available
def test_matplotlib_backend_supported_formats(backend: MatplotlibBackend) -> None:
    assert backend.supported_formats == frozenset({"png", "svg", "pdf", "jpg", "jpeg"})


# --- render ---


@matplotlib_available
def test_matplotlib_backend_render_histogram(backend: MatplotlibBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_cdf(backend: MatplotlibBackend) -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    assert ax.get_ylim() == pytest.approx((0, 1))


@matplotlib_available
def test_matplotlib_backend_render_histogram_density(backend: MatplotlibBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    heights = [patch.get_height() for patch in ax.patches]
    # The area under the histogram integrates to 1 when density=True.
    assert sum(heights) * (100 / 10) == pytest.approx(1.0)


@matplotlib_available
def test_matplotlib_backend_render_histogram_label(backend: MatplotlibBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    native = backend.render(spec)
    assert isinstance(native, Figure)
    ax = native.axes[0]
    assert ax.get_legend() is not None


@matplotlib_available
def test_matplotlib_backend_render_line(backend: MatplotlibBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_scatter(backend: MatplotlibBackend) -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@matplotlib_available
def test_matplotlib_backend_render_layer(backend: MatplotlibBackend) -> None:
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
def test_matplotlib_backend_render_grid(backend: MatplotlibBackend) -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, Figure)
    assert len(native.axes) == 2
    assert len(native.axes[0].lines) == 1
    assert len(native.axes[1].collections) == 1


@matplotlib_available
def test_matplotlib_backend_render_forwards_kwargs(backend: MatplotlibBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    native = backend.render(spec, linewidth=5)
    assert native.axes[0].lines[0].get_linewidth() == 5


@matplotlib_available
def test_matplotlib_backend_render_unsupported_spec(backend: MatplotlibBackend) -> None:
    with pytest.raises(NotImplementedError, match="No matplotlib renderer registered"):
        backend.render(cast("Any", object()))


@matplotlib_available
def test_matplotlib_backend_render_does_not_register_with_pyplot(
    backend: MatplotlibBackend,
) -> None:
    # Regression test: rendering must not go through ``pyplot.subplots()``,
    # which registers the figure with pyplot's global figure manager and
    # keeps it alive (a leak) until ``plt.close()`` is called explicitly.
    # Building the figure directly via the ``Figure`` constructor avoids
    # that registration entirely, so ``pyplot`` should never see it.
    before = set(plt.get_fignums())
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    backend.render(spec)
    assert set(plt.get_fignums()) == before


# --- save ---


@matplotlib_available
def test_matplotlib_backend_save_unsupported_format(
    backend: MatplotlibBackend, tmp_path: Path
) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.txt", "txt")


@pytest.mark.parametrize("fmt", ["png", "svg", "pdf", "jpg", "jpeg"])
@matplotlib_available
def test_matplotlib_backend_save_supported_formats(
    backend: MatplotlibBackend, tmp_path: Path, fmt: str
) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / f"fig.{fmt}"
    backend.save(native, path, fmt)
    assert path.is_file()


@matplotlib_available
def test_matplotlib_backend_save_grid(backend: MatplotlibBackend, tmp_path: Path) -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    native = backend.render(spec)
    path = tmp_path / "grid.png"
    backend.save(native, path, "png")
    assert path.is_file()


@matplotlib_available
def test_matplotlib_backend_capabilities(backend: MatplotlibBackend) -> None:
    caps = backend.capabilities()
    assert caps.backend_name == "matplotlib"
    assert SlopeSpec in caps.spec_types
    assert caps.caveats == ()


@matplotlib_available
def test_matplotlib_backend_show_non_interactive_warns(backend: MatplotlibBackend) -> None:
    # Regression test: ``Figure.show`` raised ``AttributeError`` on a figure
    # built without pyplot.
    native = backend.render(HistogramSpec(values=np.arange(101), bins=10))
    with pytest.warns(UserWarning, match="non-interactive"):
        backend.show(native)
    plt.close("all")


@matplotlib_available
def test_matplotlib_backend_show_keeps_the_figure_saveable(
    backend: MatplotlibBackend, tmp_path: Path
) -> None:
    native = backend.render(HistogramSpec(values=np.arange(101), bins=10))
    with pytest.warns(UserWarning, match="non-interactive"):
        backend.show(native)
    backend.save(native, tmp_path / "out.png", "png")
    plt.close("all")
    assert (tmp_path / "out.png").exists()


@matplotlib_available
def test_matplotlib_backend_mimebundle_keys(backend: MatplotlibBackend) -> None:
    native = backend.render(HistogramSpec(values=np.arange(101), bins=10))
    assert list(cast("dict[str, Any]", backend.mimebundle(native))) == ["image/png"]


@matplotlib_available
def test_matplotlib_backend_mimebundle_is_base64_png(backend: MatplotlibBackend) -> None:
    native = backend.render(HistogramSpec(values=np.arange(101), bins=10))
    png = base64.b64decode(cast("dict[str, Any]", backend.mimebundle(native))["image/png"])
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


@matplotlib_available
def test_matplotlib_backend_mimebundle_grid(backend: MatplotlibBackend) -> None:
    native = backend.render(GridSpec(cells=(HistogramSpec(values=np.arange(101)),)))
    assert list(cast("dict[str, Any]", backend.mimebundle(native))) == ["image/png"]
