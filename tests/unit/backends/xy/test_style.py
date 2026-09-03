from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, LineSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from plotmux.backends.xy.histogram import render_histogram
    from plotmux.backends.xy.line import render_line
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
def test_apply_common_style_ymin_ymax() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, ymin=0.0, ymax=5.0)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    y_axis = out.children[2]
    assert y_axis.domain == (0.0, 5.0)


@xy_available
def test_apply_common_style_single_ybound_ignored() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, ymin=0.0)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    y_axis = out.children[2]
    assert y_axis.domain is None


@xy_available
def test_apply_common_style_xmin_xmax() -> None:
    # ``LineSpec`` rather than ``HistogramSpec``: ``HistogramSpec.xmin``/
    # ``.xmax`` is a different, quantile-capable field (see
    # ``plotmux.specs.base.XBoundSpec``), resolved and applied by
    # ``render_histogram`` itself, not the plain, explicit-value-only
    # ``BaseSpec``-shared ``xmin``/``xmax`` under test here.
    spec = LineSpec(x=np.arange(10), y=np.arange(10), xmin=0.0, xmax=5.0)
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    x_axis = out.children[1]
    assert x_axis.domain == (0.0, 5.0)


@xy_available
def test_apply_common_style_single_xbound_ignored() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), xmin=0.0)
    chart = render_line(spec)
    out = apply_common_style(chart, spec)
    x_axis = out.children[1]
    assert x_axis.domain is None


@xy_available
def test_apply_common_style_histogram_xbounds_not_reapplied() -> None:
    # ``HistogramSpec``/``CdfSpec`` are not ``XBoundSpec`` (see
    # ``plotmux.specs.base.XBoundSpec``): their own ``xmin``/``xmax`` may
    # hold an unresolved quantile string, so ``apply_common_style`` must
    # not read them -- doing so used to crash the moment either bound was
    # set to a quantile string like ``"q0.1"``.
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin="q0.1", xmax="q0.9")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    x_axis = out.children[1]
    assert x_axis.domain is None


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


@xy_available
def test_apply_common_style_legend_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_title="Lines")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert len(out.children) == len(chart.children) + 3
    assert out.children[-1].title == "Lines"


@xy_available
def test_apply_common_style_no_legend_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert len(out.children) == len(chart.children) + 2


@xy_available
def test_apply_common_style_legend_location() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_location="top_left")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert len(out.children) == len(chart.children) + 3
    assert out.children[-1].loc == "top_left"


@xy_available
def test_apply_common_style_legend_title_and_location() -> None:
    spec = HistogramSpec(
        values=np.arange(101), bins=10, legend_title="Lines", legend_location="top_left"
    )
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert len(out.children) == len(chart.children) + 3
    assert out.children[-1].title == "Lines"
    assert out.children[-1].loc == "top_left"


@xy_available
def test_apply_common_style_legend_orientation_horizontal_sets_ncols() -> None:
    import xy

    spec = HistogramSpec(values=np.arange(101), bins=10, legend_orientation="horizontal")
    chart = xy.bar_chart(xy.bar([1, 2], [3, 4], name="a"), xy.bar([1, 2], [5, 6], name="b"))
    out = apply_common_style(chart, spec)
    assert out.children[-1].ncols == 2


@xy_available
def test_apply_common_style_no_legend_orientation_default_ncols() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_location="top_left")
    chart = render_histogram(spec)
    out = apply_common_style(chart, spec)
    assert out.children[-1].ncols == 1
