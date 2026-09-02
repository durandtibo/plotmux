from __future__ import annotations

import pytest

from plotmux.specs import SlopeSpec

################################
#     Tests for SlopeSpec     #
################################


def test_slope_spec_defaults() -> None:
    spec = SlopeSpec(gradient=2)
    assert spec.gradient == 2
    assert spec.intercept == 0.0
    assert spec.label is None
    assert spec.color is None
    assert spec.linewidth is None
    assert spec.linestyle == "solid"
    assert spec.alpha is None


def test_slope_spec_custom() -> None:
    spec = SlopeSpec(
        gradient=2,
        intercept=10,
        label="my-slope",
        color="#0000ff",
        linewidth=4,
        linestyle="dashed",
        alpha=0.9,
    )
    assert spec.gradient == 2
    assert spec.intercept == 10
    assert spec.label == "my-slope"
    assert spec.color == (0.0, 0.0, 1.0, 1.0)
    assert spec.linewidth == 4
    assert spec.linestyle == "dashed"
    assert spec.alpha == 0.9


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_slope_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        SlopeSpec(gradient=1, alpha=alpha)


# --- color parsing ---


def test_slope_spec_color_named() -> None:
    spec = SlopeSpec(gradient=1, color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_slope_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        SlopeSpec(gradient=1, color="not-a-color")


# --- common style ---


def test_slope_spec_common_style() -> None:
    spec = SlopeSpec(gradient=1, title="t", xlabel="x", ylabel="y", xscale="log", yscale="log")
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


# --- frozen ---


def test_slope_spec_is_frozen() -> None:
    spec = SlopeSpec(gradient=1)
    with pytest.raises(AttributeError):
        spec.gradient = 2


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_slope_spec_alpha_boundary_values(alpha: float) -> None:
    assert SlopeSpec(gradient=1, alpha=alpha).alpha == alpha


def test_slope_spec_negative_gradient() -> None:
    spec = SlopeSpec(gradient=-3.0)
    assert spec.gradient == -3.0


def test_slope_spec_zero_gradient() -> None:
    spec = SlopeSpec(gradient=0.0)
    assert spec.gradient == 0.0


def test_slope_spec_ymin_greater_than_ymax_raises() -> None:
    with pytest.raises(ValueError, match="ymin must not be greater than ymax"):
        SlopeSpec(gradient=1, ymin=10, ymax=0)
