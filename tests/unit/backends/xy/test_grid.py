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
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    import xy

    from plotmux.backends.xy.grid import XyGrid, render_grid, render_grid_html

################################
#     Tests for render_grid    #
################################


@xy_available
def test_render_grid_returns_xy_grid() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    grid = render_grid(spec)
    assert isinstance(grid, XyGrid)


@xy_available
def test_render_grid_one_chart_per_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    grid = render_grid(spec)
    assert len(grid.charts) == 2
    assert all(isinstance(chart, xy.Chart) for chart in grid.charts)


@xy_available
def test_render_grid_ncols() -> None:
    spec = GridSpec(
        cells=tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(4)),
        ncols=2,
    )
    grid = render_grid(spec)
    assert grid.ncols == 2


@xy_available
def test_render_grid_title() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="my grid")
    grid = render_grid(spec)
    assert grid.title == "my grid"


@xy_available
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
    assert len(grid.charts) == 1


@xy_available
def test_render_grid_with_histogram() -> None:
    spec = GridSpec(cells=(HistogramSpec(values=np.arange(101), bins=10),))
    grid = render_grid(spec)
    assert len(grid.charts) == 1


@xy_available
def test_render_grid_supports_cdf_spec() -> None:
    spec = GridSpec(cells=(CdfSpec(values=np.arange(101)),))
    grid = render_grid(spec)
    assert len(grid.charts) == 1


@xy_available
def test_render_grid_rejects_unsupported_spec_type() -> None:
    class _Unsupported:
        pass

    spec = GridSpec.__new__(GridSpec)
    object.__setattr__(spec, "cells", (_Unsupported(),))
    object.__setattr__(spec, "ncols", 1)
    object.__setattr__(spec, "title", None)
    with pytest.raises(NotImplementedError, match="No xy renderer registered"):
        render_grid(spec)


#####################################
#     Tests for render_grid_html    #
#####################################


@xy_available
def test_render_grid_html_embeds_one_iframe_per_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    page = render_grid_html(render_grid(spec))
    assert page.count("<iframe") == 2


@xy_available
def test_render_grid_html_includes_title() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="my grid")
    page = render_grid_html(render_grid(spec))
    assert "my grid" in page


@xy_available
def test_render_grid_html_omits_title_heading_when_unset() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    page = render_grid_html(render_grid(spec))
    assert "<h1>" not in page
