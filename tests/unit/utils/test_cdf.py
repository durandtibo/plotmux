from __future__ import annotations

import numpy as np
import pytest

from plotmux.utils.cdf import _binned_steps, _exact_steps, _height, _restrict, cdf_steps

VALUES = np.array([3.0, 1.0, 2.0, 4.0])

##############################
#     Tests for cdf_steps    #
##############################


def test_cdf_steps_exact_x() -> None:
    x, _ = cdf_steps(VALUES)
    assert np.array_equal(x, np.array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]))


def test_cdf_steps_exact_y() -> None:
    _, y = cdf_steps(VALUES)
    assert np.array_equal(y, np.array([0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0]))


def test_cdf_steps_binned_x() -> None:
    x, _ = cdf_steps(np.arange(5.0), nbins=2)
    assert np.array_equal(x, np.array([0.0, 0.0, 2.0, 2.0, 4.0]))


def test_cdf_steps_binned_y() -> None:
    _, y = cdf_steps(np.arange(5.0), nbins=2)
    assert np.array_equal(y, np.array([0.0, 0.4, 0.4, 1.0, 1.0]))


def test_cdf_steps_binned_has_bounded_size() -> None:
    x, _ = cdf_steps(np.arange(1000.0), nbins=10)
    assert x.shape == (21,)


def test_cdf_steps_range_does_not_renormalize() -> None:
    # P(X <= 3) is 0.75 whatever the range: the curve is cut, not rescaled.
    _, y = cdf_steps(VALUES, xmin=2.0, xmax=3.0)
    assert np.array_equal(y, np.array([0.25, 0.5, 0.5, 0.75]))


def test_cdf_steps_range_x() -> None:
    x, _ = cdf_steps(VALUES, xmin=2.0, xmax=3.0)
    assert np.array_equal(x, np.array([2.0, 2.0, 3.0, 3.0]))


def test_cdf_steps_xmin_between_values_adds_a_vertex() -> None:
    x, y = cdf_steps(VALUES, xmin=2.5)
    assert (x[0], y[0]) == (2.5, 0.5)


def test_cdf_steps_xmax_between_values_adds_a_vertex() -> None:
    x, y = cdf_steps(VALUES, xmax=2.5)
    assert (x[-1], y[-1]) == (2.5, 0.5)


def test_cdf_steps_single_value() -> None:
    x, y = cdf_steps(np.array([5.0]))
    assert (x.tolist(), y.tolist()) == ([5.0, 5.0], [0.0, 1.0])


def test_cdf_steps_duplicate_values() -> None:
    _, y = cdf_steps(np.array([1.0, 1.0]))
    assert y.tolist() == [0.0, 0.5, 0.5, 1.0]


def test_cdf_steps_does_not_change_the_input() -> None:
    values = np.array([3.0, 1.0, 2.0])
    cdf_steps(values)
    assert values.tolist() == [3.0, 1.0, 2.0]


def test_cdf_steps_is_deterministic() -> None:
    assert np.array_equal(cdf_steps(VALUES)[0], cdf_steps(VALUES)[0])


def test_cdf_steps_integer_values_give_float_vertices() -> None:
    x, _ = cdf_steps(np.array([2, 1]))
    assert x.dtype == np.float64


#################################
#     Tests for _exact_steps    #
#################################


def test_exact_steps_whole_output() -> None:
    assert [a.tolist() for a in _exact_steps(np.array([2.0, 1.0]))] == [
        [1.0, 1.0, 2.0, 2.0],
        [0.0, 0.5, 0.5, 1.0],
    ]


###################################
#     Tests for _binned_steps     #
###################################


def test_binned_steps_whole_output() -> None:
    assert [a.tolist() for a in _binned_steps(np.arange(5.0), 2)] == [
        [0.0, 0.0, 2.0, 2.0, 4.0],
        [0.0, 0.4, 0.4, 1.0, 1.0],
    ]


##############################
#     Tests for _restrict    #
##############################

X = np.array([0.0, 1.0, 2.0])
Y = np.array([0.0, 0.5, 1.0])


def test_restrict_without_bounds_returns_the_input() -> None:
    x, _ = _restrict(X, Y, None, None)
    assert x is X


def test_restrict_xmin() -> None:
    assert [a.tolist() for a in _restrict(X, Y, 0.5, None)] == [[0.5, 1.0, 2.0], [0.0, 0.5, 1.0]]


def test_restrict_xmax() -> None:
    assert [a.tolist() for a in _restrict(X, Y, None, 1.5)] == [[0.0, 1.0, 1.5], [0.0, 0.5, 0.5]]


def test_restrict_bound_on_a_vertex_adds_nothing() -> None:
    assert [a.tolist() for a in _restrict(X, Y, 1.0, 2.0)] == [[1.0, 2.0], [0.5, 1.0]]


def test_restrict_bounds_beyond_the_curve() -> None:
    assert [a.tolist() for a in _restrict(X, Y, -1.0, 3.0)] == [
        [-1.0, 0.0, 1.0, 2.0, 3.0],
        [0.0, 0.0, 0.5, 1.0, 1.0],
    ]


def test_restrict_range_between_two_vertices() -> None:
    assert [a.tolist() for a in _restrict(X, Y, 1.2, 1.8)] == [[1.2, 1.8], [0.5, 0.5]]


###########################
#     Tests for _height   #
###########################


@pytest.mark.parametrize(
    ("at", "expected"), [(-1.0, 0.0), (0.0, 0.0), (0.5, 0.0), (1.0, 0.5), (1.5, 0.5), (2.0, 1.0)]
)
def test_height(at: float, expected: float) -> None:
    assert _height(np.array([0.0, 1.0, 1.0, 2.0]), np.array([0.0, 0.0, 0.5, 1.0]), at) == expected
