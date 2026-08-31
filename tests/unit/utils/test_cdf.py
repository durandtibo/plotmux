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
