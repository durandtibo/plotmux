from __future__ import annotations

import numpy as np

from plotmux.specs import CdfSpec
from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    from xy import Chart

    from plotmux.backends.xy.cdf import render_cdf

################################
#     Tests for render_cdf     #
################################


@xy_available
def test_render_cdf_returns_chart() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_single_bin() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=1)
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_label() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, label="my-label")
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_no_color_uses_backend_default() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_color() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, color="red")
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_explicit_range() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, xmin=5, xmax=50)
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_default_nbins() -> None:
    spec = CdfSpec(values=np.arange(101))
    chart = render_cdf(spec)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_forwards_kwargs() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec, opacity=0.5)
    assert isinstance(chart, Chart)


@xy_available
def test_render_cdf_alpha() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, alpha=0.5)
    chart = render_cdf(spec)
    assert chart.children[0].props["opacity"] == 0.5
