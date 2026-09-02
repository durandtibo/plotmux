from __future__ import annotations

import numpy as np

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.histogram import render_histogram

######################################
#     Tests for render_histogram     #
######################################


@altair_available
def test_render_histogram_returns_chart() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_histogram_single_bin() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=1)
    chart = render_histogram(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_histogram_density() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    chart = render_histogram(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_histogram_label() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    chart = render_histogram(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "label"


@altair_available
def test_render_histogram_no_label_no_color_encoding() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    assert "color" not in chart.to_dict()["encoding"]


@altair_available
def test_render_histogram_no_color_uses_backend_default() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_histogram_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, color="red")
    chart = render_histogram(spec)
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_histogram_explicit_range() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin=5, xmax=50)
    chart = render_histogram(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_histogram_forwards_kwargs() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec, opacity=0.5)
    assert chart.to_dict()["mark"]["opacity"] == 0.5


@altair_available
def test_render_histogram_alpha() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, alpha=0.5)
    chart = render_histogram(spec)
    assert chart.to_dict()["mark"]["opacity"] == 0.5
