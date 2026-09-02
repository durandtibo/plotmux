from __future__ import annotations

from plotmux.specs import SlopeSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.slope import render_slope

##################################
#     Tests for render_slope     #
##################################


@matplotlib_available
def test_render_slope_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10)
    out = render_slope(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_slope_draws_one_line() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10)
    render_slope(ax, spec)
    assert len(ax.lines) == 1
    plt.close(fig)


@matplotlib_available
def test_render_slope_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10, label="my-label")
    render_slope(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_slope_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10)
    render_slope(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_slope_color() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10, color="red")
    render_slope(ax, spec)
    assert ax.lines[0].get_color() == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_render_slope_linewidth_and_linestyle() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10, linewidth=4, linestyle="dashed")
    render_slope(ax, spec)
    assert ax.lines[0].get_linewidth() == 4
    assert ax.lines[0].get_linestyle() == "--"
    plt.close(fig)


@matplotlib_available
def test_render_slope_is_an_axline() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10)
    render_slope(ax, spec)
    # ``Axes.axline`` returns an ``AxLine`` artist, not a plain ``Line2D``:
    # unlike a data-bound ``LineSpec`` (``Axes.plot``), its rendered extent
    # tracks the axes' view limits as they change rather than staying fixed
    # to two originally-computed points.
    assert type(ax.lines[0]).__name__ == "AxLine"
    plt.close(fig)


@matplotlib_available
def test_render_slope_forwards_kwargs() -> None:
    fig, ax = plt.subplots()
    spec = SlopeSpec(gradient=2, intercept=10)
    render_slope(ax, spec, linestyle=":")
    assert ax.lines[0].get_linestyle() == ":"
    plt.close(fig)
