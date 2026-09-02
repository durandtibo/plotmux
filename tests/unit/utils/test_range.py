from __future__ import annotations

import math

import numpy as np
import pytest

from plotmux.utils.range import find_range

################################
#     Tests for find_range     #
################################


# --- empty / boundary inputs ---


def test_find_range_empty() -> None:
    xmin, xmax = find_range(np.array([]))
    assert math.isnan(xmin)
    assert math.isnan(xmax)


def test_find_range_single_value() -> None:
    assert find_range(np.array([42.0])) == (42.0, 42.0)


def test_find_range_ignores_nan_values() -> None:
    values = np.array([1.0, 2.0, 3.0, np.nan])
    assert find_range(values) == (1.0, 3.0)


# --- default / explicit bounds ---


def test_find_range_default() -> None:
    assert find_range(np.arange(101)) == (0, 100)


@pytest.mark.parametrize(
    ("xmin", "xmax", "expected"),
    [
        pytest.param(5, 50, (5, 50), id="explicit_xmin_xmax"),
        pytest.param(5, None, (5, 100), id="explicit_xmin_only"),
        pytest.param(None, 50, (0, 50), id="explicit_xmax_only"),
        pytest.param("q0.1", "q0.9", (10.0, 90.0), id="quantile_xmin_xmax"),
        pytest.param("q0.1", None, (10.0, 100), id="quantile_xmin_only"),
        pytest.param(None, "q0.9", (0, 90.0), id="quantile_xmax_only"),
        pytest.param("q0", "q1", (0.0, 100.0), id="quantile_bounds"),
    ],
)
def test_find_range_bounds(
    xmin: float | str | None, xmax: float | str | None, expected: tuple
) -> None:
    assert find_range(np.arange(101), xmin=xmin, xmax=xmax) == expected


# --- error cases ---


@pytest.mark.parametrize("bound", ["0.1", "qq0.1", "q", "qabc"])
def test_find_range_invalid_quantile_string_xmin(bound: str) -> None:
    with pytest.raises(ValueError, match="Invalid quantile string"):
        find_range(np.arange(101), xmin=bound)


@pytest.mark.parametrize("bound", ["0.9", "qq0.9", "q", "qabc"])
def test_find_range_invalid_quantile_string_xmax(bound: str) -> None:
    with pytest.raises(ValueError, match="Invalid quantile string"):
        find_range(np.arange(101), xmax=bound)


@pytest.mark.parametrize("quantile", ["q-0.1", "q1.1"])
def test_find_range_quantile_out_of_range(quantile: str) -> None:
    with pytest.raises(ValueError, match="quantile must be in the range"):
        find_range(np.arange(101), xmin=quantile)


def test_find_range_lo_greater_than_hi_raises() -> None:
    with pytest.raises(
        ValueError, match="the resolved lower bound must not be greater than"
    ):
        find_range(np.arange(101), xmin=50, xmax=10)


def test_find_range_lo_greater_than_hi_quantiles_raises() -> None:
    with pytest.raises(
        ValueError, match="the resolved lower bound must not be greater than"
    ):
        find_range(np.arange(101), xmin="q0.9", xmax="q0.1")
