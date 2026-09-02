from __future__ import annotations

import numpy as np
import pytest

import plotmux
from plotmux.specs import (
    BarSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
    SlopeSpec,
)
from plotmux.testing.fixtures import bokeh_available, matplotlib_available, xy_available

##########################
#     Tests for hist     #
##########################


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
def test_hist_default_kwargs() -> None:
    fig = plotmux.hist(np.arange(101))
    assert fig.spec.bins == 30
    assert fig.spec.density is False
    assert fig.spec.color is None


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


#########################
#     Tests for cdf     #
#########################


@matplotlib_available
def test_cdf_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.cdf(np.arange(101), nbins=10)
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, CdfSpec)
    assert fig.spec.nbins == 10


@matplotlib_available
def test_cdf_explicit_backend() -> None:
    fig = plotmux.cdf(np.arange(101), nbins=10, backend="matplotlib")
    assert fig.backend_name == "matplotlib"


@xy_available
def test_cdf_explicit_xy_backend() -> None:
    fig = plotmux.cdf(np.arange(101), nbins=10, backend="xy")
    assert fig.backend_name == "xy"
    assert fig.spec.nbins == 10


def test_cdf_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.cdf(np.arange(101), backend="does-not-exist")


@matplotlib_available
def test_cdf_default_kwargs() -> None:
    fig = plotmux.cdf(np.arange(101))
    assert fig.spec.nbins is None
    assert fig.spec.color is None
    assert fig.spec.ylabel == "cumulative probability"


@matplotlib_available
def test_cdf_common_style() -> None:
    fig = plotmux.cdf(
        np.arange(101),
        nbins=10,
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


##########################
#     Tests for line     #
##########################


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


#############################
#     Tests for scatter     #
#############################


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
def test_scatter_invalid_size_raises() -> None:
    with pytest.raises(ValueError, match="size must be a positive number"):
        plotmux.scatter(np.arange(10), np.arange(10), size=-1.0)


########################
#     Tests for bar     #
########################


@matplotlib_available
def test_bar_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.bar(np.arange(10), np.arange(10) ** 2)
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, BarSpec)


@xy_available
def test_bar_explicit_xy_backend() -> None:
    fig = plotmux.bar(np.arange(10), np.arange(10) ** 2, backend="xy")
    assert fig.backend_name == "xy"


def test_bar_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.bar(np.arange(10), np.arange(10), backend="does-not-exist")


@matplotlib_available
def test_bar_mismatched_length_raises() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        plotmux.bar(np.arange(10), np.arange(5))


@matplotlib_available
def test_bar_common_style() -> None:
    fig = plotmux.bar(
        np.arange(10),
        np.arange(10) ** 2,
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


###########################
#     Tests for slope     #
###########################


@matplotlib_available
def test_slope_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.slope(2, 10)
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, SlopeSpec)
    assert fig.spec.gradient == 2
    assert fig.spec.intercept == 10


@bokeh_available
def test_slope_explicit_bokeh_backend() -> None:
    fig = plotmux.slope(2, 10, backend="bokeh", color="blue", linewidth=4, linestyle="dashed")
    assert fig.backend_name == "bokeh"


@xy_available
def test_slope_xy_backend_unsupported() -> None:
    with pytest.raises(NotImplementedError, match="No xy renderer registered"):
        plotmux.slope(2, 10, backend="xy")


def test_slope_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.slope(2, 10, backend="does-not-exist")


@matplotlib_available
def test_slope_invalid_color_raises() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        plotmux.slope(2, 10, color="not-a-color")


###########################
#     Tests for layer     #
###########################


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
    # Not ``is line_fig.spec``: an uncolored child is replaced with an
    # equivalent copy carrying a ``LayerSpec``-assigned default color (see
    # ``plotmux.specs.layer._assign_default_colors``), so identity is not
    # preserved, only the data.
    np.testing.assert_array_equal(fig.spec.layers[0].x, line_fig.spec.x)
    np.testing.assert_array_equal(fig.spec.layers[0].y, line_fig.spec.y)
    ax = fig.native.axes[0]
    assert len(ax.lines) == 1
    assert len(ax.collections) == 1


@matplotlib_available
def test_layer_single_item() -> None:
    fig = plotmux.layer(LineSpec(x=np.arange(10), y=np.arange(10)))
    assert len(fig.spec.layers) == 1


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
def test_layer_nested_layer_item_raises() -> None:
    inner = plotmux.layer(LineSpec(x=np.arange(10), y=np.arange(10)))
    with pytest.raises(ValueError, match="layers must not contain a LayerSpec"):
        plotmux.layer(inner)


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


##########################
#     Tests for grid     #
##########################


@matplotlib_available
def test_grid_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.grid(
        HistogramSpec(values=np.arange(101), bins=10),
        LineSpec(x=np.arange(0, 100, 10), y=np.arange(10)),
        ncols=2,
    )
    assert fig.backend_name == "matplotlib"
    assert isinstance(fig.spec, GridSpec)
    assert len(fig.native.axes) == 2


@matplotlib_available
def test_grid_accepts_figure_items() -> None:
    line_fig = plotmux.line(np.arange(10), np.arange(10))
    fig = plotmux.grid(line_fig, ScatterSpec(x=np.arange(10), y=np.arange(10)))
    assert isinstance(fig.spec, GridSpec)
    assert fig.spec.cells[0] is line_fig.spec


@matplotlib_available
def test_grid_single_item() -> None:
    fig = plotmux.grid(LineSpec(x=np.arange(10), y=np.arange(10)))
    assert len(fig.spec.cells) == 1


@matplotlib_available
def test_grid_default_ncols_is_one() -> None:
    fig = plotmux.grid(
        LineSpec(x=np.arange(10), y=np.arange(10)),
        ScatterSpec(x=np.arange(10), y=np.arange(10)),
    )
    assert fig.spec.ncols == 1
    assert len(fig.native.axes) == 2


@matplotlib_available
def test_grid_hides_trailing_empty_cells() -> None:
    fig = plotmux.grid(
        LineSpec(x=np.arange(10), y=np.arange(10)),
        ScatterSpec(x=np.arange(10), y=np.arange(10)),
        HistogramSpec(values=np.arange(101), bins=10),
        ncols=2,
    )
    visible = [ax for ax in fig.native.axes if ax.get_visible()]
    hidden = [ax for ax in fig.native.axes if not ax.get_visible()]
    assert len(visible) == 3
    assert len(hidden) == 1


def test_grid_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.grid(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            backend="does-not-exist",
        )


def test_grid_empty_raises() -> None:
    with pytest.raises(ValueError, match="cells must contain at least one spec"):
        plotmux.grid()


@matplotlib_available
def test_grid_nested_grid_item_raises() -> None:
    inner = plotmux.grid(LineSpec(x=np.arange(10), y=np.arange(10)))
    with pytest.raises(ValueError, match="cells must not contain a GridSpec"):
        plotmux.grid(inner)


@matplotlib_available
def test_grid_title_becomes_suptitle() -> None:
    fig = plotmux.grid(LineSpec(x=np.arange(10), y=np.arange(10)), title="t")
    assert fig.native._suptitle.get_text() == "t"
