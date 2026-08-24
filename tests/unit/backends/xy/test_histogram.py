from __future__ import annotations

import numpy as np

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.histogram import render_histogram


@xy_available
def test_render_histogram_returns_chart() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_histogram_density() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    chart = render_histogram(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_histogram_label() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    chart = render_histogram(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_histogram_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, color="red")
    chart = render_histogram(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_histogram_explicit_range() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin=5, xmax=50)
    chart = render_histogram(spec)
    assert isinstance(chart, Chart)
