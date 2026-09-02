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
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.grid import render_grid

#################################
#     Tests for render_grid     #
#################################


@plotly_available
def test_render_grid_returns_figure() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    out = render_grid(spec)
    assert isinstance(out, go.Figure)


@plotly_available
def test_render_grid_draws_each_cell_onto_its_own_subplot() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        ),
        ncols=2,
    )
    fig = render_grid(spec)
    assert len(fig.data) == 2
    xaxes = {trace.xaxis for trace in fig.data}
    assert len(xaxes) == 2


@plotly_available
def test_render_grid_with_title() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    fig = render_grid(spec)
    assert fig.layout.title.text == "overall"


@plotly_available
def test_render_grid_cell_title_becomes_subplot_annotation() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10), title="cell-title"),))
    fig = render_grid(spec)
    assert any(ann.text == "cell-title" for ann in fig.layout.annotations)


@plotly_available
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
    fig = render_grid(spec)
    assert len(fig.data) == 2


@plotly_available
def test_render_grid_with_histogram() -> None:
    spec = GridSpec(cells=(HistogramSpec(values=np.arange(101), bins=10),))
    fig = render_grid(spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_grid_supports_cdf_spec() -> None:
    spec = GridSpec(cells=(CdfSpec(values=np.arange(101), nbins=10),))
    fig = render_grid(spec)
    assert len(fig.data) == 1


@plotly_available
def test_render_grid_unsupported_spec_raises() -> None:
    class FakeCell:
        title = None
        xlabel = None
        ylabel = None
        xscale = "linear"
        yscale = "linear"
        ymin = None
        ymax = None

    spec = GridSpec.__new__(GridSpec)
    object.__setattr__(spec, "cells", (FakeCell(),))
    object.__setattr__(spec, "ncols", 1)
    object.__setattr__(spec, "title", None)
    with pytest.raises(NotImplementedError, match="No plotly renderer registered"):
        render_grid(spec)
