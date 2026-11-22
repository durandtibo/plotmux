from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Line
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


# --- frozen ---


def test_slope_spec_is_frozen() -> None:
    spec = SlopeSpec(gradient=1)
    with pytest.raises(AttributeError):
        cast("Any", spec).gradient = 2


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_slope_spec_alpha_boundary_values(alpha: float) -> None:
    assert SlopeSpec(gradient=1, alpha=alpha).alpha == alpha


def test_slope_spec_negative_gradient() -> None:
    spec = SlopeSpec(gradient=-3.0)
    assert spec.gradient == -3.0


def test_slope_spec_zero_gradient() -> None:
    spec = SlopeSpec(gradient=0.0)
    assert spec.gradient == 0.0


########################################
#     Tests for SlopeSpec lowering     #
########################################


def test_slope_spec_requires_an_extent() -> None:
    assert SlopeSpec.requires_extent is True


def test_slope_spec_to_primitives() -> None:
    spec = SlopeSpec(
        gradient=2.0,
        intercept=1.0,
        label="a",
        color="#ff0000",
        linewidth=3.0,
        linestyle="dotted",
        alpha=0.5,
    )
    assert spec.to_primitives((0.0, 10.0)) == (
        Line(
            x=np.array([0.0, 10.0]),
            y=np.array([1.0, 21.0]),
            infinite=(2.0, 1.0),
            color=(1.0, 0.0, 0.0, 1.0),
            alpha=0.5,
            linewidth=3.0,
            linestyle="dotted",
            label="a",
        ),
    )


def test_slope_spec_to_primitives_negative_gradient() -> None:
    primitive = cast("Line", SlopeSpec(gradient=-1).to_primitives((-2.0, 2.0))[0])
    assert primitive.y.tolist() == [2.0, -2.0]


def test_slope_spec_to_primitives_without_extent_raises() -> None:
    with pytest.raises(InvalidSpecError, match="a SlopeSpec needs the x extent of its panel"):
        SlopeSpec(gradient=1.0).to_primitives(None)


def test_slope_spec_has_no_x_data() -> None:
    assert SlopeSpec(gradient=1.0).x_extent() is None


def test_slope_spec_is_categorical_is_none() -> None:
    assert SlopeSpec(gradient=1.0).is_categorical() is None
