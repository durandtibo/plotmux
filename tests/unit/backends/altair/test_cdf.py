from __future__ import annotations

import numpy as np

from plotmux.specs import CdfSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.cdf import render_cdf

################################
#     Tests for render_cdf     #
################################


@altair_available
def test_render_cdf_returns_chart() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_cdf_single_bin() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=1)
    chart = render_cdf(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_cdf_label() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, label="my-label")
    chart = render_cdf(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "label"


@altair_available
def test_render_cdf_no_label_no_color_encoding() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec)
    assert "color" not in chart.to_dict()["encoding"]


@altair_available
def test_render_cdf_no_color_uses_backend_default() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_cdf_color() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, color="red")
    chart = render_cdf(spec)
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_cdf_explicit_range() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, xmin=5, xmax=50)
    chart = render_cdf(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_cdf_default_nbins() -> None:
    spec = CdfSpec(values=np.arange(101))
    chart = render_cdf(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_cdf_forwards_kwargs() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    chart = render_cdf(spec, opacity=0.5)
    assert chart.to_dict()["mark"]["opacity"] == 0.5


@altair_available
def test_render_cdf_alpha() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, alpha=0.5)
    chart = render_cdf(spec)
    assert chart.to_dict()["mark"]["opacity"] == 0.5
