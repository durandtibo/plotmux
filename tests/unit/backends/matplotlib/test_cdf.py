from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import CdfSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.cdf import render_cdf

################################
#     Tests for render_cdf     #
################################


@matplotlib_available
def test_render_cdf_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10)
    out = render_cdf(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_cdf_ylim() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10)
    render_cdf(ax, spec)
    assert ax.get_ylim() == pytest.approx((0, 1))
    plt.close(fig)


@matplotlib_available
def test_render_cdf_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10, label="my-label")
    render_cdf(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_cdf_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10)
    render_cdf(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_cdf_explicit_range() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10, xmin=5, xmax=50)
    render_cdf(ax, spec)
    assert ax.get_xlim() == pytest.approx((5, 50))
    plt.close(fig)


@matplotlib_available
def test_render_cdf_color() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10, color="red")
    render_cdf(ax, spec)
    assert ax.patches[0].get_edgecolor() == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_cdf_default_nbins() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101))
    out = render_cdf(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_cdf_forwards_kwargs() -> None:
    fig, ax = plt.subplots()
    spec = CdfSpec(values=np.arange(101), nbins=10)
    render_cdf(ax, spec, alpha=0.3)
    assert ax.patches[0].get_alpha() == 0.3
    plt.close(fig)
