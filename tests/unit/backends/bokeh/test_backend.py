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
)
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if TYPE_CHECKING:
    from pathlib import Path

if is_bokeh_available():
    from bokeh.models import Column, GridPlot, LogScale
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.backend import BokehBackend


@pytest.fixture
def backend() -> BokehBackend:
    return BokehBackend()


#################################
#     Tests for BokehBackend     #
#################################


@bokeh_available
def test_bokeh_backend_name(backend: BokehBackend) -> None:
    assert backend.name == "bokeh"


@bokeh_available
def test_bokeh_backend_supported_formats(backend: BokehBackend) -> None:
    assert backend.supported_formats == frozenset({"html"})


# --- render ---


@bokeh_available
def test_bokeh_backend_render_histogram(backend: BokehBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, figure)


@bokeh_available
def test_bokeh_backend_render_histogram_density(backend: BokehBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, figure)


@bokeh_available
def test_bokeh_backend_render_cdf(backend: BokehBackend) -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    native = backend.render(spec)
    assert isinstance(native, figure)
    assert native.y_range.start == 0
    assert native.y_range.end == 1


@bokeh_available
def test_bokeh_backend_render_line(backend: BokehBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, figure)


@bokeh_available
def test_bokeh_backend_render_scatter(backend: BokehBackend) -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, figure)


@bokeh_available
def test_bokeh_backend_render_layer(backend: BokehBackend) -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, figure)
    assert len(native.renderers) == 2


@bokeh_available
def test_bokeh_backend_render_grid_without_title(backend: BokehBackend) -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, GridPlot)


@bokeh_available
def test_bokeh_backend_render_grid_with_title(backend: BokehBackend) -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    native = backend.render(spec)
    assert isinstance(native, Column)


@bokeh_available
def test_bokeh_backend_render_applies_common_style(backend: BokehBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    native = backend.render(spec)
    assert native.title.text == "my-title"


@bokeh_available
def test_bokeh_backend_render_log_scale(backend: BokehBackend) -> None:
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale="log", yscale="log")
    native = backend.render(spec)
    assert isinstance(native.x_scale, LogScale)
    assert isinstance(native.y_scale, LogScale)


@bokeh_available
def test_bokeh_backend_render_unsupported_spec(backend: BokehBackend) -> None:
    with pytest.raises(NotImplementedError, match="No bokeh renderer registered"):
        backend.render(object())


# --- save ---


@bokeh_available
def test_bokeh_backend_save_unsupported_format(backend: BokehBackend, tmp_path: Path) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.png", "png")


@bokeh_available
def test_bokeh_backend_save_html(backend: BokehBackend, tmp_path: Path) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / "fig.html"
    backend.save(native, path, "html")
    assert path.is_file()
    assert path.stat().st_size > 0


@bokeh_available
def test_bokeh_backend_save_grid_with_title(backend: BokehBackend, tmp_path: Path) -> None:
    # Regression test: a ``GridSpec``'s ``column`` layout has no ``.title``
    # attribute at all (unlike a plain ``figure``), so ``save`` must not
    # assume one is always present.
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    native = backend.render(spec)
    path = tmp_path / "grid.html"
    backend.save(native, path, "html")
    assert path.is_file()
    assert path.stat().st_size > 0
