from __future__ import annotations

import numpy as np

from plotmux.utils.categorical import is_categorical

#####################################
#     Tests for is_categorical     #
#####################################


def test_is_categorical_string_array() -> None:
    assert is_categorical(np.array(["a", "b", "c"]))


def test_is_categorical_numeric_int_array() -> None:
    assert not is_categorical(np.arange(3))


def test_is_categorical_numeric_float_array() -> None:
    assert not is_categorical(np.array([1.0, 2.0, 3.0]))


def test_is_categorical_empty_string_array() -> None:
    assert is_categorical(np.array([], dtype=str))


def test_is_categorical_empty_numeric_array() -> None:
    assert not is_categorical(np.array([]))
