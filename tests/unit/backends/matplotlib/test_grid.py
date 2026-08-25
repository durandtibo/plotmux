from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import GridSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    from plotmux.backends.matplotlib.grid import render_grid

#################################
#     Tests for render_grid     #
#################################


@matplotlib_available
def test_render_grid_one_axes_per_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    fig = render_grid(spec)
    assert len(fig.axes) == 2


@matplotlib_available
def test_render_grid_draws_each_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    fig = render_grid(spec)
    assert len(fig.axes[0].lines) == 1
    assert len(fig.axes[1].collections) == 1


@matplotlib_available
def test_render_grid_ncols_layout() -> None:
    spec = GridSpec(
        cells=tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(4)),
        ncols=2,
    )
    fig = render_grid(spec)
    axes = fig.axes
    assert len(axes) == 4
    # 4 cells over 2 columns should form a 2x2 grid.
    assert all(ax.get_visible() for ax in axes)


@matplotlib_available
def test_render_grid_hides_trailing_empty_axes() -> None:
    spec = GridSpec(
        cells=tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(3)),
        ncols=2,
    )
    fig = render_grid(spec)
    visible = [ax for ax in fig.axes if ax.get_visible()]
    hidden = [ax for ax in fig.axes if not ax.get_visible()]
    assert len(visible) == 3
    assert len(hidden) == 1


@matplotlib_available
def test_render_grid_each_cell_keeps_own_style() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10), title="a"),
            ScatterSpec(x=np.arange(10), y=np.arange(10), title="b"),
        )
    )
    fig = render_grid(spec)
    assert fig.axes[0].get_title() == "a"
    assert fig.axes[1].get_title() == "b"


@matplotlib_available
def test_render_grid_title_becomes_suptitle() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    fig = render_grid(spec)
    assert fig._suptitle.get_text() == "overall"


@matplotlib_available
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
    assert len(fig.axes[0].lines) == 1
    assert len(fig.axes[0].collections) == 1


@matplotlib_available
def test_render_grid_with_histogram() -> None:
    spec = GridSpec(cells=(HistogramSpec(values=np.arange(101), bins=10),))
    fig = render_grid(spec)
    assert len(fig.axes[0].patches) == 10


@matplotlib_available
def test_render_grid_forwards_kwargs_to_every_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            LineSpec(x=np.arange(10), y=np.arange(10) + 1),
        )
    )
    fig = render_grid(spec, linewidth=5)
    assert fig.axes[0].lines[0].get_linewidth() == 5
    assert fig.axes[1].lines[0].get_linewidth() == 5


@matplotlib_available
def test_render_grid_unsupported_spec_raises() -> None:
    spec = GridSpec.__new__(GridSpec)
    object.__setattr__(spec, "cells", (object(),))
    object.__setattr__(spec, "ncols", 1)
    object.__setattr__(spec, "title", None)
    with pytest.raises(NotImplementedError, match="No matplotlib renderer registered"):
        render_grid(spec)
