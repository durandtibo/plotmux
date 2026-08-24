from __future__ import annotations

import numpy as np

from plotmux.specs import HistogramSpec
from plotmux.testing.fixtures import bokeh_available
from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from bokeh.plotting import figure

    from plotmux.backends.bokeh.histogram import render_histogram

######################################
#     Tests for render_histogram     #
######################################


@bokeh_available
def test_render_histogram_returns_figure() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = figure()
    out = render_histogram(fig, spec)
    assert out is fig


@bokeh_available
def test_render_histogram_single_bin() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=1)
    fig = render_histogram(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_histogram_density() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, density=True)
    fig = render_histogram(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_histogram_label() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, label="my-label")
    fig = render_histogram(figure(), spec)
    assert len(fig.legend) == 1


@bokeh_available
def test_render_histogram_no_label_no_legend() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(figure(), spec)
    assert len(fig.legend) == 0


@bokeh_available
def test_render_histogram_no_color_uses_backend_default() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_histogram_color() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, color="red")
    fig = render_histogram(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_histogram_explicit_range() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin=5, xmax=50)
    fig = render_histogram(figure(), spec)
    assert isinstance(fig, figure)


@bokeh_available
def test_render_histogram_forwards_kwargs() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=10)
    fig = render_histogram(figure(), spec, fill_alpha=0.5)
    assert isinstance(fig, figure)
