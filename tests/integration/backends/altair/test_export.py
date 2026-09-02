r"""End-to-end export coverage: every chart type x every altair export
format, plus a layered figure, through the full public-API ->
``Figure.save`` -> ``export.save`` -> ``Backend.save`` pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

import plotmux
from plotmux.specs import HistogramSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import altair_available

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.figure import Figure

FORMATS = ["html", "json"]


def _hist() -> Figure:
    return plotmux.hist(np.arange(101), bins=10, backend="altair")


def _bar() -> Figure:
    return plotmux.bar(np.arange(10), np.arange(10) ** 2, backend="altair")


def _line() -> Figure:
    return plotmux.line(np.arange(10), np.arange(10) ** 2, backend="altair")


def _scatter() -> Figure:
    return plotmux.scatter(np.arange(10), np.arange(10) ** 2, backend="altair")


def _layer() -> Figure:
    return plotmux.layer(
        HistogramSpec(values=np.arange(101), bins=10),
        LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        ScatterSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        backend="altair",
    )


@altair_available
@pytest.mark.parametrize("make_figure", [_hist, _bar, _line, _scatter, _layer])
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
