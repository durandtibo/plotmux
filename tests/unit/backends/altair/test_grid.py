from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import GridSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.grid import render_grid

#################################
#     Tests for render_grid     #
#################################


@altair_available
def test_render_grid_returns_concat_chart() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    chart = render_grid(spec)
    assert isinstance(chart, alt.ConcatChart)


@altair_available
def test_render_grid_one_subchart_per_cell() -> None:
    spec = GridSpec(
        cells=(
            LineSpec(x=np.arange(10), y=np.arange(10)),
            ScatterSpec(x=np.arange(10), y=np.arange(10)),
        )
    )
    chart = render_grid(spec)
    assert len(chart.concat) == 2


@altair_available
def test_render_grid_ncols() -> None:
    spec = GridSpec(
        cells=tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(4)),
        ncols=2,
    )
    chart = render_grid(spec)
    assert chart.columns == 2


@altair_available
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
    chart = render_grid(spec)
    assert isinstance(chart.concat[0], alt.LayerChart)


@altair_available
def test_render_grid_with_histogram() -> None:
    spec = GridSpec(cells=(HistogramSpec(values=np.arange(101), bins=10),))
    chart = render_grid(spec)
    assert len(chart.concat) == 1


@altair_available
def test_render_grid_title() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), title="overall")
    chart = render_grid(spec)
    assert chart.title == "overall"


@altair_available
def test_render_grid_unsupported_spec_raises() -> None:
    spec = GridSpec.__new__(GridSpec)
    object.__setattr__(spec, "cells", (object(),))
    object.__setattr__(spec, "ncols", 1)
    object.__setattr__(spec, "title", None)
    with pytest.raises(NotImplementedError, match="No altair renderer registered"):
        render_grid(spec)
