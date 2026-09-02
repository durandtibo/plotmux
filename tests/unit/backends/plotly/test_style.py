from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import plotly_available
from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    import plotly.graph_objects as go

    from plotmux.backends.plotly.style import apply_common_style, rgba_to_plotly

########################################
#     Tests for rgba_to_plotly     #
########################################


def _rgba_to_plotly_cases() -> list:
    return [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
        pytest.param((1.0, 1.0, 1.0, 1.0), "rgba(255, 255, 255, 1.0)", id="white"),
    ]


@pytest.mark.parametrize(("color", "expected"), _rgba_to_plotly_cases())
@plotly_available
def test_rgba_to_plotly(color: tuple[float, float, float, float], expected: str) -> None:
    assert rgba_to_plotly(color) == expected


#########################################
#     Tests for apply_common_style     #
#########################################


@plotly_available
def test_apply_common_style_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    fig = go.Figure()
    out = apply_common_style(fig, spec)
    assert out.layout.title.text == "my-title"


@plotly_available
def test_apply_common_style_no_title() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = go.Figure()
    out = apply_common_style(fig, spec)
    assert out.layout.title.text is None


@plotly_available
def test_apply_common_style_labels() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xlabel="x", ylabel="y")
    fig = apply_common_style(go.Figure(), spec)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "y"


@plotly_available
def test_apply_common_style_no_labels() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = apply_common_style(go.Figure(), spec)
    assert fig.layout.xaxis.title.text is None
    assert fig.layout.yaxis.title.text is None


@plotly_available
def test_apply_common_style_background_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, background_color="lightgray")
    fig = apply_common_style(go.Figure(), spec)
    assert fig.layout.plot_bgcolor is not None


@plotly_available
def test_apply_common_style_both_ybounds() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, ymin=0, ymax=5)
    fig = apply_common_style(go.Figure(), spec)
    assert tuple(fig.layout.yaxis.range) == (0, 5)


@plotly_available
def test_apply_common_style_single_ybound_ignored() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, ymin=0)
    fig = apply_common_style(go.Figure(), spec)
    assert fig.layout.yaxis.range is None


@plotly_available
def test_apply_common_style_log_scale() -> None:
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale="log", yscale="log")
    fig = apply_common_style(go.Figure(), spec)
    assert fig.layout.xaxis.type == "log"
    assert fig.layout.yaxis.type == "log"


@plotly_available
def test_apply_common_style_returns_same_figure() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = go.Figure()
    out = apply_common_style(fig, spec)
    assert out is fig
