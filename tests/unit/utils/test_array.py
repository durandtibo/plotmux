from __future__ import annotations

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.utils import to_paired_arrays, to_readonly_array

#######################################
#     Tests for to_readonly_array     #
#######################################


def test_to_readonly_array_values() -> None:
    assert np.array_equal(to_readonly_array([1, 2, 3]), np.array([1, 2, 3]))


def test_to_readonly_array_is_read_only() -> None:
    assert not to_readonly_array(np.arange(3)).flags.writeable


def test_to_readonly_array_assignment_raises() -> None:
    array = to_readonly_array(np.arange(3))
    with pytest.raises(ValueError, match="read-only"):
        array[0] = 1


def test_to_readonly_array_does_not_share_memory() -> None:
    a = np.arange(3)
    assert not np.shares_memory(to_readonly_array(a), a)


def test_to_readonly_array_input_change_is_not_seen() -> None:
    a = np.arange(3)
    b = to_readonly_array(a)
    a[0] = 99
    assert b[0] == 0


def test_to_readonly_array_does_not_freeze_the_input() -> None:
    a = np.arange(3)
    to_readonly_array(a)
    assert a.flags.writeable


def test_to_readonly_array_read_only_input_is_copied() -> None:
    a = np.arange(3)
    a.flags.writeable = False
    assert not np.shares_memory(to_readonly_array(a), a)


def test_to_readonly_array_empty() -> None:
    assert to_readonly_array([]).shape == (0,)


def test_to_readonly_array_preserves_dtype() -> None:
    assert to_readonly_array(np.array([1.5, 2.5], dtype=np.float32)).dtype == np.float32


def test_to_readonly_array_preserves_shape() -> None:
    assert to_readonly_array(np.ones((2, 3))).shape == (2, 3)


######################################
#     Tests for to_paired_arrays     #
######################################


def test_to_paired_arrays_same_length() -> None:
    x, y = to_paired_arrays(np.arange(5), np.arange(5))
    assert x.shape == y.shape == (5,)


def test_to_paired_arrays_different_length_raises() -> None:
    with pytest.raises(
        InvalidSpecError, match=r"x and y must have the same length, but received 5 and 3"
    ):
        to_paired_arrays(np.arange(5), np.arange(3))


def test_to_paired_arrays_x_not_1d_raises() -> None:
    with pytest.raises(InvalidSpecError, match="x and y must be 1-dimensional"):
        to_paired_arrays(np.zeros((5, 3)), np.arange(5))


def test_to_paired_arrays_y_not_1d_raises() -> None:
    with pytest.raises(InvalidSpecError, match="x and y must be 1-dimensional"):
        to_paired_arrays(np.arange(5), np.zeros((5, 3)))


def test_to_paired_arrays_converts_lists() -> None:
    x, _ = to_paired_arrays([1, 2, 3], [4, 5, 6])
    assert np.array_equal(x, np.array([1, 2, 3]))


def test_to_paired_arrays_empty_arrays() -> None:
    x, _ = to_paired_arrays(np.array([]), np.array([]))
    assert x.shape == (0,)


def test_to_paired_arrays_x_is_read_only() -> None:
    x, _ = to_paired_arrays(np.arange(3), np.arange(3))
    assert not x.flags.writeable


def test_to_paired_arrays_y_is_read_only() -> None:
    _, y = to_paired_arrays(np.arange(3), np.arange(3))
    assert not y.flags.writeable


def test_to_paired_arrays_does_not_share_memory() -> None:
    a = np.arange(3)
    x, _ = to_paired_arrays(a, a)
    assert not np.shares_memory(x, a)
