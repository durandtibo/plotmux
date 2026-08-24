from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import LineSpec


def test_line_spec_defaults() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    assert spec.label is None
    assert spec.color is None


def test_line_spec_custom() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-line", color="#ff0000")
    assert spec.label == "my-line"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_line_spec_color_named() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_line_spec_color_rgba_tuple() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_line_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        LineSpec(x=np.arange(10), y=np.arange(10), color="not-a-color")


def test_line_spec_is_frozen() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(AttributeError):
        spec.label = "new-label"


def test_line_spec_mismatched_length() -> None:
    with pytest.raises(ValueError, match="x and y must have the same length"):
        LineSpec(x=np.arange(10), y=np.arange(5))


def test_line_spec_common_style() -> None:
    spec = LineSpec(
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
