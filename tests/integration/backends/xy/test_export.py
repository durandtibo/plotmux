r"""End-to-end export coverage: every chart type x every xy export
format, plus a layered figure, through the full public-API ->
``Figure.save`` -> ``export.save`` -> ``Backend.save`` pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

import plotmux
from plotmux.specs import HistogramSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import xy_available

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.figure import Figure

FORMATS = ["png", "jpg", "jpeg", "webp", "svg", "pdf", "html"]


def _hist() -> Figure:
    return plotmux.hist(np.arange(101), bins=10, backend="xy")


def _line() -> Figure:
    return plotmux.line(np.arange(10), np.arange(10) ** 2, backend="xy")


def _scatter() -> Figure:
    return plotmux.scatter(np.arange(10), np.arange(10) ** 2, backend="xy")


def _layer() -> Figure:
    return plotmux.layer(
        HistogramSpec(values=np.arange(101), bins=10),
        LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        ScatterSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        backend="xy",
    )


@xy_available
@pytest.mark.parametrize("make_figure", [_hist, _line, _scatter, _layer])
@pytest.mark.parametrize("fmt", FORMATS)
def test_save_chart_type_format_matrix(
    make_figure,  # noqa: ANN001
    fmt: str,
    tmp_path: Path,
) -> None:
    fig = make_figure()
    path = tmp_path / f"fig.{fmt}"
    fig.save(path)
    assert path.is_file()
    assert path.stat().st_size > 0


@xy_available
def test_save_grid_html(tmp_path: Path) -> None:
    # ``GridSpec`` is HTML-only for xy: unlike the other three backends, xy
    # has no chart-composition primitive suited to arranging independent
    # panels, so it cannot be rasterized into PNG/SVG/PDF -- see
    # ``plotmux.backends.xy.grid.XyGrid``.
    fig = plotmux.grid(
        HistogramSpec(values=np.arange(101), bins=10),
        LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        ncols=2,
        backend="xy",
    )
    path = tmp_path / "fig.html"
    fig.save(path)
    assert path.is_file()
    assert path.stat().st_size > 0
