from __future__ import annotations

import numpy as np

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.style import apply_common_style


@matplotlib_available
def test_apply_common_style_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    out = apply_common_style(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_title() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    apply_common_style(ax, spec)
    assert ax.get_title() == "my-title"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_title() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_title() == ""
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_labels() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, xlabel="x", ylabel="y")
    apply_common_style(ax, spec)
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_default_scale_is_linear() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_xscale() == "linear"
    assert ax.get_yscale() == "linear"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_log_scale() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale="log", yscale="log")
    apply_common_style(ax, spec)
    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
    plt.close(fig)
