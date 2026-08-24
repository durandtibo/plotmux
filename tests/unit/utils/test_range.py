from __future__ import annotations

import math

import numpy as np
import pytest

from plotmux.utils.range import find_range


def test_find_range_empty() -> None:
    xmin, xmax = find_range(np.array([]))
    assert math.isnan(xmin)
    assert math.isnan(xmax)


def test_find_range_default() -> None:
    assert find_range(np.arange(101)) == (0, 100)


def test_find_range_explicit_xmin_xmax() -> None:
    assert find_range(np.arange(101), xmin=5, xmax=50) == (5, 50)


def test_find_range_explicit_xmin_only() -> None:
    assert find_range(np.arange(101), xmin=5) == (5, 100)


def test_find_range_explicit_xmax_only() -> None:
    assert find_range(np.arange(101), xmax=50) == (0, 50)


def test_find_range_quantile_xmin_xmax() -> None:
    assert find_range(np.arange(101), xmin="q0.1", xmax="q0.9") == (10.0, 90.0)


def test_find_range_quantile_xmin_only() -> None:
    assert find_range(np.arange(101), xmin="q0.1") == (10.0, 100)


def test_find_range_quantile_xmax_only() -> None:
    assert find_range(np.arange(101), xmax="q0.9") == (0, 90.0)


def test_find_range_quantile_bounds() -> None:
    assert find_range(np.arange(101), xmin="q0", xmax="q1") == (0.0, 100.0)


def test_find_range_ignores_nan_values() -> None:
    values = np.array([1.0, 2.0, 3.0, np.nan])
    assert find_range(values) == (1.0, 3.0)


def test_find_range_single_value() -> None:
    assert find_range(np.array([42.0])) == (42.0, 42.0)


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
