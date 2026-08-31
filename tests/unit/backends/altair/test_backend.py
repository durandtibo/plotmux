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
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if TYPE_CHECKING:
    from pathlib import Path

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.backend import AltairBackend


@pytest.fixture
def backend() -> AltairBackend:
    return AltairBackend()


#####################################
#     Tests for AltairBackend     #
#####################################


@altair_available
def test_altair_backend_name(backend: AltairBackend) -> None:
    assert backend.name == "altair"


@altair_available
def test_altair_backend_supported_formats(backend: AltairBackend) -> None:
    assert backend.supported_formats == frozenset({"html", "json"})


# --- render ---


@altair_available
def test_altair_backend_render_histogram(backend: AltairBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    assert isinstance(native, alt.Chart)


@altair_available
def test_altair_backend_render_histogram_density(backend: AltairBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    native = backend.render(spec)
    assert isinstance(native, alt.Chart)


@altair_available
def test_altair_backend_render_cdf(backend: AltairBackend) -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    native = backend.render(spec)
    assert isinstance(native, alt.Chart)


@altair_available
def test_altair_backend_render_line(backend: AltairBackend) -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, alt.Chart)


@altair_available
def test_altair_backend_render_scatter(backend: AltairBackend) -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2)
    native = backend.render(spec)
    assert isinstance(native, alt.Chart)


@altair_available
def test_altair_backend_render_layer(backend: AltairBackend) -> None:
    spec = LayerSpec(
        layers=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        )
    )
    native = backend.render(spec)
    assert isinstance(native, alt.LayerChart)
    assert len(native.layer) == 2


@altair_available
def test_altair_backend_render_grid(backend: AltairBackend) -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10) ** 2),
            ScatterSpec(x=np.arange(10), y=np.arange(10) ** 2),
        ),
        ncols=2,
    )
    native = backend.render(spec)
    assert isinstance(native, alt.ConcatChart)
    assert len(native.concat) == 2
    assert native.columns == 2


@altair_available
def test_altair_backend_render_applies_common_style(backend: AltairBackend) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    native = backend.render(spec)
    assert native.to_dict()["title"] == "my-title"


@altair_available
def test_altair_backend_render_log_scale(backend: AltairBackend) -> None:
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale="log", yscale="log")
    native = backend.render(spec)
    encoding = native.to_dict()["encoding"]
    assert encoding["x"]["scale"]["type"] == "log"
    assert encoding["y"]["scale"]["type"] == "log"


@altair_available
def test_altair_backend_render_unsupported_spec(backend: AltairBackend) -> None:
    with pytest.raises(NotImplementedError, match="No altair renderer registered"):
        backend.render(object())


# --- save ---


@altair_available
def test_altair_backend_save_unsupported_format(backend: AltairBackend, tmp_path: Path) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    with pytest.raises(ValueError, match="Unsupported export format"):
        backend.save(native, tmp_path / "fig.png", "png")


@pytest.mark.parametrize("fmt", ["html", "json"])
@altair_available
def test_altair_backend_save_supported_formats(
    backend: AltairBackend, tmp_path: Path, fmt: str
) -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    native = backend.render(spec)
    path = tmp_path / f"fig.{fmt}"
    backend.save(native, path, fmt)
    assert path.is_file()
    assert path.stat().st_size > 0


@altair_available
def test_altair_backend_save_grid(backend: AltairBackend, tmp_path: Path) -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    native = backend.render(spec)
    path = tmp_path / "grid.html"
    backend.save(native, path, "html")
    assert path.is_file()
    assert path.stat().st_size > 0
