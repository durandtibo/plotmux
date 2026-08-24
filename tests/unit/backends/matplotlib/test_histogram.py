from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.histogram import render_histogram


@matplotlib_available
def test_render_histogram_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    out = render_histogram(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_histogram_bins() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    render_histogram(ax, spec)
    assert len(ax.patches) == 10
    plt.close(fig)


@matplotlib_available
def test_render_histogram_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    render_histogram(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_histogram_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    render_histogram(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_histogram_density() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    render_histogram(ax, spec)
    heights = [patch.get_height() for patch in ax.patches]
    assert sum(heights) * (100 / 10) == pytest.approx(1.0)
    plt.close(fig)


@matplotlib_available
def test_render_histogram_explicit_range() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin=5, xmax=50)
    render_histogram(ax, spec)
    assert ax.get_xlim() == pytest.approx((5, 50), abs=5)
    plt.close(fig)
