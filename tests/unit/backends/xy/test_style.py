from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from plotmux.backends.xy.histogram import render_histogram
    from plotmux.backends.xy.style import apply_common_style, rgba_to_xy

##################################
#     Tests for rgba_to_xy     #
##################################


def _rgba_to_xy_cases() -> list:
    return [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
        pytest.param((1.0, 1.0, 1.0, 1.0), "rgba(255, 255, 255, 1.0)", id="white"),
    ]


@pytest.mark.parametrize(("color", "expected"), _rgba_to_xy_cases())
@xy_available
def test_rgba_to_xy(color: tuple[float, float, float, float], expected: str) -> None:
    assert rgba_to_xy(color) == expected


#########################################
#     Tests for apply_common_style     #
#########################################


@xy_available
def test_apply_common_style_keeps_mark() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.children[0] is chart.children[0]


@xy_available
def test_apply_common_style_appends_axes() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert len(out.children) == len(chart.children) + 2


@xy_available
def test_apply_common_style_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.title == "my-title"


@xy_available
def test_apply_common_style_no_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.title is None


@xy_available
def test_apply_common_style_labels_and_scale() -> None:
    spec = HistogramSpec(
        values=np.arange(101), bins=10, xlabel="x", ylabel="y", xscale="log", yscale="linear"
    )
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    x_axis, y_axis = out.children[1], out.children[2]
    assert x_axis.label == "x"
    assert x_axis.type_ == "log"
    assert y_axis.label == "y"
    assert y_axis.type_ == "linear"


@xy_available
def test_apply_common_style_no_labels() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    x_axis, y_axis = out.children[1], out.children[2]
    assert x_axis.label is None
    assert y_axis.label is None


@xy_available
def test_apply_common_style_preserves_layout() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.width == chart.width
    assert out.height == chart.height
    assert out.padding == chart.padding


@xy_available
def test_apply_common_style_background_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, background_color="red")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.style["backgroundColor"] == "rgba(255, 0, 0, 1.0)"


@xy_available
def test_apply_common_style_no_background_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert not out.style
