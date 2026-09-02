from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import GridSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec

###############################
#     Tests for GridSpec     #
###############################


def test_grid_spec_cells() -> None:
    hist_spec = HistogramSpec(values=np.arange(101), bins=10)
    line_spec = LineSpec(x=np.arange(10), y=np.arange(10))
    spec = GridSpec(cells=(hist_spec, line_spec))
    assert spec.cells == (hist_spec, line_spec)


def test_grid_spec_default_ncols() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    assert spec.ncols == 1


def test_grid_spec_explicit_ncols() -> None:
    children = tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(5))
    spec = GridSpec(cells=children, ncols=2)
    assert spec.ncols == 2
    assert len(spec.cells) == 5


def test_grid_spec_accepts_layer_spec_cell() -> None:
    inner = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    spec = GridSpec(cells=(inner, ScatterSpec(x=np.arange(10), y=np.arange(10))))
    assert spec.cells[0] is inner


def test_grid_spec_common_style() -> None:
    spec = GridSpec(
        cells=(LineSpec(x=np.arange(10), y=np.arange(10)),),
        title="t",
    )
    assert spec.title == "t"


# --- frozen / error cases ---


def test_grid_spec_is_frozen() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(AttributeError):
        spec.cells = ()


def test_grid_spec_empty_cells_raises() -> None:
    with pytest.raises(ValueError, match="cells must contain at least one spec"):
        GridSpec(cells=())


def test_grid_spec_nested_grid_raises() -> None:
    inner = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(ValueError, match="cells must not contain a GridSpec"):
        GridSpec(cells=(inner,))


def test_grid_spec_nested_grid_among_other_children_raises() -> None:
    inner = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    other = ScatterSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(ValueError, match="cells must not contain a GridSpec"):
        GridSpec(cells=(other, inner))


def test_grid_spec_non_positive_ncols_raises() -> None:
    with pytest.raises(ValueError, match="ncols must be a positive integer"):
        GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=0)


@pytest.mark.parametrize("ncols", [-1, -10])
def test_grid_spec_negative_ncols_raises(ncols: int) -> None:
    with pytest.raises(ValueError, match="ncols must be a positive integer"):
        GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=ncols)


def test_grid_spec_non_integer_ncols_raises() -> None:
    with pytest.raises(ValueError, match="ncols must be a positive integer"):
        GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=2.5)


def test_grid_spec_bool_ncols_raises() -> None:
    # bool is an Integral subclass, but it must not be accepted as ncols.
    with pytest.raises(ValueError, match="ncols must be a positive integer"):
        GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=True)


def test_grid_spec_numpy_integer_ncols_accepted() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=np.int64(3))
    assert spec.ncols == 3


def test_grid_spec_ncols_larger_than_cells_does_not_raise() -> None:
    spec = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),), ncols=5)
    assert spec.ncols == 5
    assert len(spec.cells) == 1
