from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LineSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    from plotmux.backends.altair.histogram import render_histogram
    from plotmux.backends.altair.line import render_line
    from plotmux.backends.altair.style import (
        apply_common_style,
        color_encoding,
        prepare_color,
        rgba_to_altair,
        with_label_field,
    )

######################################
#     Tests for rgba_to_altair     #
######################################


def _rgba_to_altair_cases() -> list:
    return [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
        pytest.param((1.0, 1.0, 1.0, 1.0), "rgba(255, 255, 255, 1.0)", id="white"),
    ]


@pytest.mark.parametrize(("color", "expected"), _rgba_to_altair_cases())
@altair_available
def test_rgba_to_altair(color: tuple[float, float, float, float], expected: str) -> None:
    assert rgba_to_altair(color) == expected


##########################################
#     Tests for with_label_field     #
##########################################


@altair_available
def test_with_label_field_none_returns_same_data() -> None:
    data = [{"x": 1, "y": 1}]
    assert with_label_field(data, None) is data


@altair_available
def test_with_label_field_adds_field() -> None:
    data = [{"x": 1, "y": 1}, {"x": 2, "y": 2}]
    out = with_label_field(data, "my-label")
    assert out == [{"x": 1, "y": 1, "label": "my-label"}, {"x": 2, "y": 2, "label": "my-label"}]


########################################
#     Tests for color_encoding     #
########################################


@altair_available
def test_color_encoding_no_label_returns_none() -> None:
    assert color_encoding("red", None) is None
    assert color_encoding(None, None) is None


@altair_available
def test_color_encoding_label_no_color() -> None:
    encoding = color_encoding(None, "my-label")
    assert encoding.shorthand == "label:N"


@altair_available
def test_color_encoding_label_and_color() -> None:
    encoding = color_encoding("red", "my-label")
    assert encoding.shorthand == "label:N"
    assert encoding.to_dict()["scale"]["range"] == ["red"]


####################################
#     Tests for prepare_color     #
####################################


@altair_available
def test_prepare_color_no_label_no_color() -> None:
    data = [{"x": 1, "y": 1}]
    kwargs = {}
    out_data, encoding = prepare_color(data, None, None, kwargs)
    assert out_data is data
    assert encoding is None
    assert kwargs == {}


@altair_available
def test_prepare_color_no_label_with_color_sets_kwarg() -> None:
    data = [{"x": 1, "y": 1}]
    kwargs = {}
    out_data, encoding = prepare_color(data, None, "red", kwargs)
    assert out_data is data
    assert encoding is None
    assert kwargs == {"color": "red"}


@altair_available
def test_prepare_color_label_adds_field_and_encoding() -> None:
    data = [{"x": 1, "y": 1}]
    kwargs = {}
    out_data, encoding = prepare_color(data, "my-label", "red", kwargs)
    assert out_data == [{"x": 1, "y": 1, "label": "my-label"}]
    assert encoding.shorthand == "label:N"
    assert kwargs == {}


#########################################
#     Tests for apply_common_style     #
#########################################


@altair_available
def test_apply_common_style_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.to_dict()["title"] == "my-title"


@altair_available
def test_apply_common_style_no_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert "title" not in out.to_dict()


@altair_available
def test_apply_common_style_labels_and_scale() -> None:
    spec = LineSpec(
        x=np.arange(10), y=np.arange(10), xlabel="x", ylabel="y", xscale="log", yscale="linear"
    )
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    encoding = out.to_dict()["encoding"]
    assert encoding["x"]["title"] == "x"
    assert encoding["x"]["scale"]["type"] == "log"
    assert encoding["y"]["title"] == "y"
    assert encoding["y"]["scale"]["type"] == "linear"


@altair_available
def test_apply_common_style_no_labels() -> None:
    # ``title=None`` is passed explicitly (rather than omitted) so Vega-Lite
    # hides the axis title instead of falling back to its own default
    # (the capitalized field name, e.g. "X") -- see
    # ``apply_common_style``'s docstring.
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    encoding = out.to_dict()["encoding"]
    assert encoding["x"]["title"] is None
    assert encoding["y"]["title"] is None


@altair_available
def test_apply_common_style_ymin_ymax() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), ymin=0.0, ymax=5.0)
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    scale = out.to_dict()["encoding"]["y"]["scale"]
    assert scale["domainMin"] == 0.0
    assert scale["domainMax"] == 5.0


@altair_available
def test_apply_common_style_no_ymin_ymax() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    scale = out.to_dict()["encoding"]["y"]["scale"]
    assert "domainMin" not in scale
    assert "domainMax" not in scale


@altair_available
def test_apply_common_style_background_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, background_color="red")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.to_dict()["background"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_apply_common_style_no_background_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert "background" not in out.to_dict()


@altair_available
def test_apply_common_style_legend_title() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="s", legend_title="Lines")
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    assert out.to_dict()["encoding"]["color"]["legend"]["title"] == "Lines"


@altair_available
def test_apply_common_style_no_legend_title() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    assert "color" not in out.to_dict()["encoding"]
