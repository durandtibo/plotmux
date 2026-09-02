from __future__ import annotations

import numpy as np

from plotmux.specs import CdfSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.cdf import render_cdf

################################
#     Tests for render_cdf     #
################################


@bokeh_available
def test_render_cdf_returns_figure() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = figure()
    out = render_cdf(fig, spec)
    assert out is fig


@bokeh_available
def test_render_cdf_y_range() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = render_cdf(figure(), spec)
    assert fig.y_range.start == 0
    assert fig.y_range.end == 1


@bokeh_available
def test_render_cdf_label() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, label="my-label")
    fig = render_cdf(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_cdf_no_label_no_legend() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = render_cdf(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_cdf_no_color_uses_backend_default() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = render_cdf(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_cdf_color() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, color="red")
    fig = render_cdf(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_cdf_explicit_range() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, xmin=5, xmax=50)
    fig = render_cdf(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_cdf_default_nbins() -> None:
    spec = CdfSpec(values=np.arange(101))
    fig = render_cdf(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_cdf_forwards_kwargs() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10)
    fig = render_cdf(figure(), spec, line_alpha=0.5)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_cdf_alpha() -> None:
    spec = CdfSpec(values=np.arange(101), nbins=10, alpha=0.5)
    fig = render_cdf(figure(), spec)
    assert fig.renderers[0].glyph.line_alpha == 0.5
