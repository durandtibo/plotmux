from __future__ import annotations

import numpy as np
import pytest

from plotmux.utils.extent import finite_extent

###################################
#     Tests for finite_extent     #
###################################


def test_finite_extent_float() -> None:
    assert finite_extent(np.array([3.0, 1.0, 2.0])) == (1.0, 3.0)


def test_finite_extent_integer() -> None:
    assert finite_extent(np.array([3, 1, 2])) == (1.0, 3.0)


def test_finite_extent_ignores_nan() -> None:
    assert finite_extent(np.array([1.0, np.nan, 3.0])) == (1.0, 3.0)


def test_finite_extent_single_value() -> None:
    assert finite_extent(np.array([2.0])) == (2.0, 2.0)


def test_finite_extent_pad() -> None:
    assert finite_extent(np.array([1.0, 3.0]), pad=0.5) == (0.5, 3.5)


@pytest.mark.parametrize(
    "values",
    [np.array([]), np.array([np.nan, np.nan]), np.array(["a", "b"])],
    ids=["empty", "all-nan", "strings"],
)
def test_finite_extent_none(values: np.ndarray) -> None:
    assert finite_extent(values) is None
