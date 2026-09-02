from __future__ import annotations

import numpy as np
import pytest

from plotmux.utils.cdf import compute_cdf_steps

#######################################
#     Tests for compute_cdf_steps     #
#######################################


def test_compute_cdf_steps_shape() -> None:
    x, y = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
    assert x.shape == (21,)
    assert y.shape == (21,)


def test_compute_cdf_steps_starts_at_zero() -> None:
    x, y = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
    assert x[0] == pytest.approx(0)
    assert y[0] == pytest.approx(0)


def test_compute_cdf_steps_ends_at_one() -> None:
    x, y = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
    assert x[-1] == pytest.approx(100)
    assert y[-1] == pytest.approx(1)


def test_compute_cdf_steps_is_non_decreasing() -> None:
    _, y = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
    assert np.all(np.diff(y) >= 0)


def test_compute_cdf_steps_single_bin() -> None:
    x, y = compute_cdf_steps(np.arange(101), bins=1, xmin=0, xmax=100)
    assert x.shape == (3,)
    assert y.tolist() == pytest.approx([0.0, 1.0, 1.0])


def test_compute_cdf_steps_single_value() -> None:
    x, y = compute_cdf_steps(np.array([5.0]), bins=5, xmin=0, xmax=10)
    assert x.tolist() == pytest.approx([0.0, 0.0, 2.0, 2.0, 4.0, 4.0, 6.0, 6.0, 8.0, 8.0, 10.0])
    assert y.tolist() == pytest.approx([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])


def test_compute_cdf_steps_edges_are_evenly_spaced() -> None:
    x, _ = compute_cdf_steps(np.arange(101), bins=5, xmin=0, xmax=100)
    # bin edges: 0, 20, 40, 60, 80, 100
    assert x.tolist() == pytest.approx([0, 0, 20, 20, 40, 40, 60, 60, 80, 80, 100])


def test_compute_cdf_steps_values_outside_range_are_excluded() -> None:
    # Values outside [xmin, xmax] are excluded from the histogram counts
    # (per numpy.histogram semantics), but do not affect normalization
    # since the denominator is the sum of in-range counts.
    values = np.concatenate([np.array([-100.0, 1000.0]), np.arange(101)])
    x, y = compute_cdf_steps(values, bins=10, xmin=0, xmax=100)
    x_ref, y_ref = compute_cdf_steps(np.arange(101), bins=10, xmin=0, xmax=100)
    assert x.tolist() == pytest.approx(x_ref.tolist())
    assert y.tolist() == pytest.approx(y_ref.tolist())


def test_compute_cdf_steps_negative_values() -> None:
    x, y = compute_cdf_steps(np.arange(-50, 51), bins=10, xmin=-50, xmax=50)
    assert x[0] == pytest.approx(-50)
    assert x[-1] == pytest.approx(50)
    assert y[0] == pytest.approx(0)
    assert y[-1] == pytest.approx(1)


def test_compute_cdf_steps_empty_bin_stays_flat() -> None:
    # All values fall in the lower half of the range, so the upper-half
    # bins should contribute no additional cumulative mass (flat plateau).
    values = np.zeros(10)
    x, y = compute_cdf_steps(values, bins=2, xmin=0, xmax=10)
    assert x.tolist() == pytest.approx([0, 0, 5, 5, 10])
    assert y.tolist() == pytest.approx([0.0, 1.0, 1.0, 1.0, 1.0])
