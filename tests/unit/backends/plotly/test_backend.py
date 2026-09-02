from __future__ import annotations

from typing import TYPE_CHECKING

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
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if TYPE_CHECKING:
    from pathlib import Path

if is_plotly_available():
    from plotly.graph_objects import Figure

    from plotmux.backends.plotly.backend import PlotlyBackend


@pytest.fixture
def backend() -> PlotlyBackend:
    return PlotlyBackend()


##################################
#     Tests for PlotlyBackend     #
##################################


@plotly_available
def test_plotly_backend_name(backend: PlotlyBackend) -> None:
    assert backend.name == "plotly"


@plotly_available
def test_plotly_backend_supported_formats(backend: PlotlyBackend) -> None:
    assert backend.supported_formats == frozenset({"html", "json"})


# --- render ---


@plotly_available
def test_plotly_backend_render_histogram(backend: PlotlyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@plotly_available
def test_plotly_backend_render_histogram_density(backend: PlotlyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@plotly_available
def test_plotly_backend_render_cdf(backend: PlotlyBackend) -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    native = backend.render(spec)
    assert isinstance(native, Figure)
    assert tuple(native.layout.yaxis.range) == (0, 1)


@plotly_available
def test_plotly_backend_render_line(backend: PlotlyBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@plotly_available
def test_plotly_backend_render_scatter(backend: PlotlyBackend) -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, Figure)


@plotly_available
def test_plotly_backend_render_layer(backend: PlotlyBackend) -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, Figure)
    assert len(native.data) == 2


@plotly_available
def test_plotly_backend_render_layer_with_slope() -> None:
    backend = PlotlyBackend()
    spec = LayerSpec(
        layers=(
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
            SlopeSpec(gradient=2, intercept=10),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, Figure)
    assert len(native.data) == 2


@plotly_available
def test_plotly_backend_render_standalone_slope_unsupported(backend: PlotlyBackend) -> None:
    with pytest.raises(NotImplementedError, match="No plotly renderer registered"):
        backend.render(SlopeSpec(gradient=2, intercept=10))


@plotly_available
def test_plotly_backend_render_grid(backend: PlotlyBackend) -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        ),
        ncols=2,
    )
    native = backend.render(spec)
    assert isinstance(native, Figure)
    assert len(native.data) == 2


@plotly_available
def test_plotly_backend_render_grid_with_title(backend: PlotlyBackend) -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    native = backend.render(spec)
    assert native.layout.title.text == "overall"


@plotly_available
def test_plotly_backend_render_applies_common_style(backend: PlotlyBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    native = backend.render(spec)
    assert native.layout.title.text == "my-title"


@plotly_available
def test_plotly_backend_render_log_scale(backend: PlotlyBackend) -> None:
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale="log", yscale="log")
    native = backend.render(spec)
    assert native.layout.xaxis.type == "log"
    assert native.layout.yaxis.type == "log"


@plotly_available
def test_plotly_backend_render_unsupported_spec(backend: PlotlyBackend) -> None:
    with pytest.raises(NotImplementedError, match="No plotly renderer registered"):
        backend.render(object())


# --- save ---


@plotly_available
def test_plotly_backend_save_unsupported_format(backend: PlotlyBackend, tmp_path: Path) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.png", "png")


@plotly_available
@pytest.mark.parametrize("fmt", ["html", "json"])
def test_plotly_backend_save_supported_formats(
    backend: PlotlyBackend, tmp_path: Path, fmt: str
) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / f"fig.{fmt}"
    backend.save(native, path, fmt)
    assert path.is_file()
    assert path.stat().st_size > 0
