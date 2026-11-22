from __future__ import annotations

import numpy as np
import pytest

from plotmux.utils import to_readonly_array

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
