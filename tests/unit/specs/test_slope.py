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


def test_slope_spec_custom() -> None:
    spec = SlopeSpec(
        gradient=2,
        intercept=10,
        label="my-slope",
        color="#0000ff",
        linewidth=4,
        linestyle="dashed",
    )
    assert spec.gradient == 2
    assert spec.intercept == 10
    assert spec.label == "my-slope"
    assert spec.color == (0.0, 0.0, 1.0, 1.0)
    assert spec.linewidth == 4
    assert spec.linestyle == "dashed"


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
