from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.colors import RGB
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.style import apply_common_style, rgba_to_bokeh

######################################
#     Tests for rgba_to_bokeh     #
######################################


def _rgba_to_bokeh_cases() -> list:
    return [
        pytest.param((1.0, 0.0, 0.0, 1.0), RGB(255, 0, 0, 1.0), id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), RGB(0, 0, 0, 0.0), id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), RGB(128, 128, 128, 0.5), id="rounding"),
        pytest.param((1.0, 1.0, 1.0, 1.0), RGB(255, 255, 255, 1.0), id="white"),
    ]


@pytest.mark.parametrize(("color", "expected"), _rgba_to_bokeh_cases())
@bokeh_available
def test_rgba_to_bokeh(color: tuple[float, float, float, float], expected: RGB) -> None:
    out = rgba_to_bokeh(color)
    assert (out.r, out.g, out.b, out.a) == (expected.r, expected.g, expected.b, expected.a)


#########################################
#     Tests for apply_common_style     #
#########################################


@bokeh_available
def test_apply_common_style_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    fig = figure()
    out = apply_common_style(fig, spec)
    assert out.title.text == "my-title"


@bokeh_available
def test_apply_common_style_no_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = figure()
    out = apply_common_style(fig, spec)
    assert out.title.text == ""


@bokeh_available
def test_apply_common_style_labels() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xlabel="x", ylabel="y")
    fig = figure()
    out = apply_common_style(fig, spec)
    assert out.xaxis.axis_label == "x"
    assert out.yaxis.axis_label == "y"


@bokeh_available
def test_apply_common_style_no_labels() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = figure()
    out = apply_common_style(fig, spec)
    assert out.xaxis.axis_label is None
    assert out.yaxis.axis_label is None


@bokeh_available
def test_apply_common_style_returns_same_figure() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = figure()
    out = apply_common_style(fig, spec)
    assert out is fig
