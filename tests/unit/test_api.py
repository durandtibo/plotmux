from __future__ import annotations

import numpy as np
import pytest

import plotmux
from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available, xy_available


@matplotlib_available
def test_hist_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10)
    assert fig.backend_name == "matplotlib"
    assert fig.spec.bins == 10


@matplotlib_available
def test_hist_explicit_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10, backend="matplotlib")
    assert fig.backend_name == "matplotlib"


@xy_available
def test_hist_explicit_xy_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10, backend="xy")
    assert fig.backend_name == "xy"
    assert fig.spec.bins == 10


def test_hist_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.hist(np.arange(101), backend="does-not-exist")


@matplotlib_available
def test_hist_common_style() -> None:
    fig = plotmux.hist(
        np.arange(101),
        bins=10,
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert fig.spec.title == "t"
    assert fig.spec.xlabel == "x"
    assert fig.spec.ylabel == "y"
    assert fig.spec.xscale == "log"
    assert fig.spec.yscale == "log"
    ax = fig.native.axes[0]
    assert ax.get_title() == "t"
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"


@matplotlib_available
def test_line_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.line(np.arange(10), np.arange(10) ** 2)
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, LineSpec)


@xy_available
def test_line_explicit_xy_backend() -> None:
    fig = plotmux.line(np.arange(10), np.arange(10) ** 2, backend="xy")
    assert fig.backend_name == "xy"


def test_line_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.line(np.arange(10), np.arange(10), backend="does-not-exist")


@matplotlib_available
def test_line_mismatched_length_raises() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        plotmux.line(np.arange(10), np.arange(5))


@matplotlib_available
def test_scatter_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.scatter(np.arange(10), np.arange(10) ** 2)
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, ScatterSpec)


@xy_available
def test_scatter_explicit_xy_backend() -> None:
    fig = plotmux.scatter(np.arange(10), np.arange(10) ** 2, backend="xy")
    assert fig.backend_name == "xy"


def test_scatter_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.scatter(np.arange(10), np.arange(10), backend="does-not-exist")


@matplotlib_available
def test_scatter_mismatched_length_raises() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        plotmux.scatter(np.arange(10), np.arange(5))


@matplotlib_available
def test_layer_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.layer(
        HistogramSpec(values=np.arange(101), bins=10),
        LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
    )
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, LayerSpec)
    ax = fig.native.axes[0]
    assert len(ax.patches) == 10
    assert len(ax.lines) == 1


@matplotlib_available
def test_layer_accepts_figure_items() -> None:
    line_fig = plotmux.line(np.arange(10), np.arange(10))
    fig = plotmux.layer(line_fig, ScatterSpec(x=np.arange(10), y=np.arange(10)))
    assert isinstance(fig.spec, LayerSpec)
    assert fig.spec.layers[0] is line_fig.spec
    ax = fig.native.axes[0]
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1


@xy_available
def test_layer_explicit_xy_backend() -> None:
    fig = plotmux.layer(
        LineSpec(x=np.arange(10), y=np.arange(10)),
        ScatterSpec(x=np.arange(10), y=np.arange(10)),
        backend="xy",
    )
    assert fig.backend_name == "xy"


def test_layer_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.layer(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            backend="does-not-exist",
        )


def test_layer_empty_raises() -> None:
    with pytest.raises(ValueError, match="layers must contain at least one spec"):
        plotmux.layer()


@matplotlib_available
def test_layer_common_style() -> None:
    fig = plotmux.layer(
        LineSpec(x=np.arange(10), y=np.arange(10)),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    ax = fig.native.axes[0]
    assert ax.get_title() == "t"
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
