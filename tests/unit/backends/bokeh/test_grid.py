from __future__ import annotations

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
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.models import Column, GridPlot

    from plotmux.backends.bokeh.grid import render_grid

#################################
#     Tests for render_grid     #
#################################


@bokeh_available
def test_render_grid_returns_gridplot_without_title() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    out = render_grid(spec)
    assert isinstance(out, GridPlot)


@bokeh_available
def test_render_grid_returns_column_with_title() -> None:
    spec = GridSpec(
        cells=(LineSpec(x=np.arange(10), y=np.arange(10)),),
        title="overall",
    )
    out = render_grid(spec)
    assert isinstance(out, Column)


@bokeh_available
def test_render_grid_draws_each_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    grid = render_grid(spec)
    figs = [child for row in grid.children for child in row if not isinstance(child, int)]
    assert len(figs) == 2
    assert all(len(f.renderers) == 1 for f in figs)


@bokeh_available
def test_render_grid_accepts_layer_spec_cell() -> None:
    spec = GridSpec(
        cells=(
            LayerSpec(
                layers=(
                    LineSpec(x=np.arange(10), y=np.arange(10)),
                    ScatterSpec(x=np.arange(10), y=np.arange(10)),
                )
            ),
        )
    )
    grid = render_grid(spec)
    fig = grid.children[0][0]
    assert len(fig.renderers) == 2


@bokeh_available
def test_render_grid_with_histogram() -> None:
    spec = GridSpec(cells=(HistogramSpec(values=np.arange(101), bins=10),))
    grid = render_grid(spec)
    fig = grid.children[0][0]
    assert len(fig.renderers) == 1


@bokeh_available
def test_render_grid_supports_cdf_spec() -> None:
    spec = GridSpec(cells=(CdfSpec(values=np.arange(101), nbins=10),))
    grid = render_grid(spec)
    fig = grid.children[0][0]
    assert len(fig.renderers) == 1


@bokeh_available
def test_render_grid_unsupported_spec_raises() -> None:
    class FakeCell:
        xscale = "linear"
        yscale = "linear"

    spec = GridSpec.__new__(GridSpec)
    object.__setattr__(spec, "cells", (FakeCell(),))
    object.__setattr__(spec, "ncols", 1)
    object.__setattr__(spec, "title", None)
    with pytest.raises(NotImplementedError, match="No bokeh renderer registered"):
        render_grid(spec)
