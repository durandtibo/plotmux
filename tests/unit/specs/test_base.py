from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidColorError, InvalidSpecError
from plotmux.specs.base import MarkSpec, Spec


@dataclass(frozen=True, eq=False)
class FakeArraySpec(Spec):
    values: np.ndarray = field(default_factory=lambda: np.arange(3))


@dataclass(frozen=True, eq=False)
class FakeMark(MarkSpec):
    value: int = 0


###########################
#     Tests for Spec      #
###########################


def test_spec_is_frozen() -> None:
    with pytest.raises(AttributeError):
        cast("Any", FakeArraySpec()).values = np.arange(2)


def test_spec_equal_with_equal_arrays() -> None:
    assert FakeArraySpec(values=np.arange(3)) == FakeArraySpec(values=np.arange(3))


def test_spec_not_equal_with_different_array_values() -> None:
    assert FakeArraySpec(values=np.arange(3)) != FakeArraySpec(values=np.arange(1, 4))


def test_spec_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'FakeArraySpec'"):
        hash(FakeArraySpec())


###############################
#     Tests for MarkSpec      #
###############################


def test_mark_spec_defaults() -> None:
    mark = FakeMark()
    assert (mark.label, mark.color, mark.alpha) == (None, None, None)


def test_mark_spec_does_not_require_an_extent() -> None:
    assert FakeMark.requires_extent is False


def test_mark_spec_style_fields_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        cast("Any", FakeMark)(0, "label")


def test_mark_spec_label() -> None:
    assert FakeMark(label="a").label == "a"


def test_mark_spec_color_hex() -> None:
    assert FakeMark(color="#ff0000").color == (1.0, 0.0, 0.0, 1.0)


def test_mark_spec_color_named() -> None:
    assert FakeMark(color="tab:blue").color == pytest.approx((31 / 255, 119 / 255, 180 / 255, 1.0))


def test_mark_spec_color_rgb_tuple() -> None:
    assert FakeMark(color=(0.5, 0.5, 0.5)).color == (0.5, 0.5, 0.5, 1.0)


def test_mark_spec_invalid_color_raises() -> None:
    with pytest.raises(InvalidColorError, match="Invalid color"):
        FakeMark(color="not-a-color")


@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
def test_mark_spec_alpha_boundaries(alpha: float) -> None:
    assert FakeMark(alpha=alpha).alpha == alpha


@pytest.mark.parametrize("alpha", [-0.1, 1.1, 2.0])
def test_mark_spec_invalid_alpha_raises(alpha: float) -> None:
    with pytest.raises(InvalidSpecError, match=r"alpha must be in the range \[0, 1\]"):
        FakeMark(alpha=alpha)


def test_mark_spec_x_extent_is_none() -> None:
    assert FakeMark().x_extent() is None


def test_mark_spec_is_categorical_is_none() -> None:
    assert FakeMark().is_categorical() is None


def test_mark_spec_to_primitives_must_be_overridden() -> None:
    with pytest.raises(NotImplementedError, match="FakeMark must implement to_primitives"):
        FakeMark().to_primitives(None)
