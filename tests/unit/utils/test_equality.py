from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from plotmux.utils.equality import ValueObject


@dataclass(frozen=True, eq=False)
class Data(ValueObject):
    values: np.ndarray
    name: str = "a"


@dataclass(frozen=True, eq=False)
class OtherData(ValueObject):
    values: np.ndarray
    name: str = "a"


#################################
#     Tests for ValueObject     #
#################################


def test_value_object_equal_with_equal_arrays() -> None:
    assert Data(np.arange(3)) == Data(np.arange(3))


def test_value_object_not_equal_with_different_array_values() -> None:
    assert Data(np.arange(3)) != Data(np.arange(1, 4))


def test_value_object_not_equal_with_different_array_lengths() -> None:
    assert Data(np.arange(3)) != Data(np.arange(4))


def test_value_object_not_equal_with_different_field() -> None:
    assert Data(np.arange(3), name="a") != Data(np.arange(3), name="b")


def test_value_object_not_equal_with_different_type() -> None:
    assert Data(np.arange(3)) != OtherData(np.arange(3))


def test_value_object_not_equal_with_other_object() -> None:
    assert Data(np.arange(3)) != "data"


def test_value_object_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'Data'"):
        hash(Data(np.arange(3)))
