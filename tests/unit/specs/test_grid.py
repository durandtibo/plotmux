from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.specs import GridSpec, HistogramSpec, LineSpec, PanelSpec

PANEL = PanelSpec(marks=(LineSpec(x=np.arange(3), y=np.arange(3)),))
OTHER = PanelSpec(marks=(HistogramSpec(values=np.arange(11.0)),))

###############################
#     Tests for GridSpec      #
###############################


def test_grid_spec_defaults() -> None:
    spec = GridSpec(panels=(PANEL,))
    assert (spec.ncols, spec.title) == (1, None)


def test_grid_spec_custom() -> None:
    spec = GridSpec(panels=(PANEL, OTHER), ncols=2, title="t")
    assert (spec.panels, spec.ncols, spec.title) == ((PANEL, OTHER), 2, "t")


def test_grid_spec_panels_list_becomes_tuple() -> None:
    assert GridSpec(panels=cast("Any", [PANEL])).panels == (PANEL,)


def test_grid_spec_is_frozen() -> None:
    with pytest.raises(AttributeError):
        cast("Any", GridSpec(panels=(PANEL,))).ncols = 2


def test_grid_spec_equal() -> None:
    assert GridSpec(panels=(PANEL,)) == GridSpec(panels=(PANEL,))


def test_grid_spec_not_equal_with_different_ncols() -> None:
    assert GridSpec(panels=(PANEL, PANEL), ncols=1) != GridSpec(panels=(PANEL, PANEL), ncols=2)


def test_grid_spec_empty_panels_raises() -> None:
    with pytest.raises(InvalidSpecError, match="panels must contain at least one panel"):
        GridSpec(panels=())


def test_grid_spec_grid_in_a_grid_raises() -> None:
    inner = GridSpec(panels=(PANEL,))
    with pytest.raises(
        InvalidSpecError, match="panels must hold PanelSpec objects, but received GridSpec"
    ):
        GridSpec(panels=cast("Any", (inner,)))


def test_grid_spec_mark_is_not_a_panel() -> None:
    with pytest.raises(InvalidSpecError, match="but received LineSpec"):
        GridSpec(panels=cast("Any", (LineSpec(x=np.arange(3), y=np.arange(3)),)))


@pytest.mark.parametrize("ncols", [0, -1, 1.5, True])
def test_grid_spec_invalid_ncols_raises(ncols: Any) -> None:
    with pytest.raises(InvalidSpecError, match="ncols must be a positive integer"):
        GridSpec(panels=(PANEL,), ncols=ncols)


def test_grid_spec_numpy_integer_ncols() -> None:
    assert GridSpec(panels=(PANEL,), ncols=cast("Any", np.int64(2))).ncols == 2
