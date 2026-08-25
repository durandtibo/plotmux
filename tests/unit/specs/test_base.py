from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from plotmux.specs.base import BaseSpec, _check_equal_length


@dataclass(frozen=True)
class FakeSpec(BaseSpec):
    value: int = 0


@dataclass(frozen=True)
class FakeColorSpec(BaseSpec):
    color: str | tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        self._normalize_color()


###############################
#     Tests for BaseSpec     #
###############################


def test_base_spec_is_dataclass() -> None:
    spec = FakeSpec(value=42)
    assert spec.value == 42


def test_base_spec_is_frozen() -> None:
    spec = FakeSpec(value=42)
    with pytest.raises(AttributeError):
        spec.value = 43


def test_base_spec_default_style() -> None:
    spec = FakeSpec(value=42)
    assert spec.title is None
    assert spec.xlabel is None
    assert spec.ylabel is None
    assert spec.xscale == "linear"
    assert spec.yscale == "linear"


def test_base_spec_custom_style() -> None:
    spec = FakeSpec(value=42, title="t", xlabel="x", ylabel="y", xscale="log", yscale="log")
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


@pytest.mark.parametrize("scale", ["linear", "log"])
def test_base_spec_xscale_values(scale: str) -> None:
    assert FakeSpec(xscale=scale).xscale == scale


@pytest.mark.parametrize("scale", ["linear", "log"])
def test_base_spec_yscale_values(scale: str) -> None:
    assert FakeSpec(yscale=scale).yscale == scale


def test_base_spec_style_fields_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        FakeSpec(0, "t")  # type: ignore[misc]


def test_base_spec_equality() -> None:
    assert FakeSpec(value=1) == FakeSpec(value=1)


def test_base_spec_inequality_on_style() -> None:
    assert FakeSpec(value=1, title="a") != FakeSpec(value=1, title="b")


##########################################
#     Tests for BaseSpec._normalize_color     #
##########################################


def test_normalize_color_leaves_none_untouched() -> None:
    spec = FakeColorSpec(color=None)
    assert spec.color is None


def test_normalize_color_parses_hex_string() -> None:
    spec = FakeColorSpec(color="#ff0000")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_normalize_color_parses_named_color() -> None:
    spec = FakeColorSpec(color="tab:blue")
    assert spec.color == pytest.approx((31 / 255, 119 / 255, 180 / 255, 1.0))


def test_normalize_color_parses_rgb_tuple() -> None:
    spec = FakeColorSpec(color=(0.5, 0.5, 0.5))
    assert spec.color == (0.5, 0.5, 0.5, 1.0)


def test_normalize_color_invalid_color_raises() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        FakeColorSpec(color="not-a-color")


##############################################
#     Tests for _check_equal_length     #
##############################################


def test_check_equal_length_same_length_does_not_raise() -> None:
    _check_equal_length(np.arange(5), np.arange(5))


def test_check_equal_length_different_length_raises() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        _check_equal_length(np.arange(5), np.arange(3))


def test_check_equal_length_non_1d_raises() -> None:
    # A 2D x with a matching leading dimension must not slip past this
    # check: it would otherwise fail deep inside a backend's plotting
    # call with a confusing, backend-specific error instead of a clear
    # InvalidSpecError here.
    with pytest.raises(ValueError, match="x and y must be 1-dimensional"):
        _check_equal_length(np.zeros((5, 3)), np.arange(5))
