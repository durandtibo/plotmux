from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import ScatterSpec

##################################
#     Tests for ScatterSpec     #
##################################


def test_scatter_spec_defaults() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None
    assert spec.size is None
    assert spec.edgecolor is None
    assert spec.alpha is None
    assert spec.marker is None


def test_scatter_spec_custom() -> None:
    spec = ScatterSpec(
        x=np.arange(10),
        y=np.arange(10),
        label="my-scatter",
        color="#ff0000",
        size=10.0,
        edgecolor="#000000",
        alpha=0.5,
        marker="square",
    )
    assert spec.label == "my-scatter"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)
    assert spec.size == 10.0
    assert spec.edgecolor == (0.0, 0.0, 0.0, 1.0)
    assert spec.alpha == 0.5
    assert spec.marker == "square"


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_scatter_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=alpha)


def test_scatter_spec_invalid_edgecolor() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor="not-a-color")


def test_scatter_spec_empty_arrays() -> None:
    spec = ScatterSpec(x=np.array([]), y=np.array([]))
    assert spec.x.shape == (0,)


def test_scatter_spec_size_small_positive_boundary() -> None:
    assert ScatterSpec(x=np.arange(10), y=np.arange(10), size=1e-9).size == 1e-9


# --- color parsing ---


def test_scatter_spec_color_named() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_scatter_spec_color_rgba_tuple() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_scatter_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


# --- common style ---


def test_scatter_spec_common_style() -> None:
    spec = ScatterSpec(
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


def test_scatter_spec_is_frozen() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        spec.label = "new-label"


def test_scatter_spec_mismatched_length() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        ScatterSpec(x=np.arange(10), y=np.arange(5))


@pytest.mark.parametrize("size", [0, -1, -10.5])
def test_scatter_spec_invalid_size(size: float) -> None:
    with pytest.raises(ValueError, match="size must be a positive number"):
        ScatterSpec(x=np.arange(10), y=np.arange(10), size=size)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_scatter_spec_alpha_boundary_values(alpha: float) -> None:
    assert ScatterSpec(x=np.arange(10), y=np.arange(10), alpha=alpha).alpha == alpha


def test_scatter_spec_edgecolor_defaults_independent_of_color() -> None:
    # edgecolor is not derived from color at the spec level (only at
    # render time), so it stays None even when color is set.
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.edgecolor is None


def test_scatter_spec_edgecolor_rgba_tuple() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), edgecolor=(0.1, 0.2, 0.3, 0.4))
    assert spec.edgecolor == (0.1, 0.2, 0.3, 0.4)
