from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import BarSpec

##############################
#     Tests for BarSpec     #
##############################


def test_bar_spec_defaults() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None
    assert spec.width == 0.8


def test_bar_spec_custom() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), label="my-bar", color="#ff0000", width=0.5)
    assert spec.label == "my-bar"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)
    assert spec.width == 0.5


def test_bar_spec_empty_arrays() -> None:
    spec = BarSpec(x=np.array([]), y=np.array([]))
    assert spec.x.shape == (0,)


def test_bar_spec_width_small_positive_boundary() -> None:
    assert BarSpec(x=np.arange(10), y=np.arange(10), width=1e-9).width == 1e-9


# --- color parsing ---


def test_bar_spec_color_named() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_bar_spec_color_rgba_tuple() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_bar_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        BarSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


# --- common style ---


def test_bar_spec_common_style() -> None:
    spec = BarSpec(
        x=np.arange(10),
        y=np.arange(10),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


# --- frozen / error cases ---


def test_bar_spec_is_frozen() -> None:
    spec = BarSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        spec.label = "new-label"


def test_bar_spec_mismatched_length() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        BarSpec(x=np.arange(10), y=np.arange(5))


@pytest.mark.parametrize("width", [0, -1, -10.5])
def test_bar_spec_invalid_width(width: float) -> None:
    with pytest.raises(ValueError, match="width must be a positive number"):
        BarSpec(x=np.arange(10), y=np.arange(10), width=width)


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_bar_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        BarSpec(x=np.arange(10), y=np.arange(10), alpha=alpha)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_bar_spec_alpha_boundary_values(alpha: float) -> None:
    assert BarSpec(x=np.arange(10), y=np.arange(10), alpha=alpha).alpha == alpha
