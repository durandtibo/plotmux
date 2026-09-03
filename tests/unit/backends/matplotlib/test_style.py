from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec, ScatterSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure as MplFigure

    from plotmux.backends.matplotlib.style import apply_common_style, attach_repr_png

#########################################
#     Tests for apply_common_style     #
#########################################


@matplotlib_available
def test_apply_common_style_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    out = apply_common_style(ax, spec)
    assert out is ax
    plt.close(fig)


# --- title ---


@matplotlib_available
def test_apply_common_style_title() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, title="my-title")
    apply_common_style(ax, spec)
    assert ax.get_title() == "my-title"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_title() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_title() == ""
    plt.close(fig)


# --- labels ---


@matplotlib_available
def test_apply_common_style_labels() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, xlabel="x", ylabel="y")
    apply_common_style(ax, spec)
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_labels() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_xlabel() == ""
    assert ax.get_ylabel() == ""
    plt.close(fig)


# --- scale ---


@matplotlib_available
def test_apply_common_style_default_scale_is_linear() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_xscale() == "linear"
    assert ax.get_yscale() == "linear"
    plt.close(fig)


@pytest.mark.parametrize("scale", ["linear", "log"])
@matplotlib_available
def test_apply_common_style_xscale(scale: str) -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, xscale=scale)
    apply_common_style(ax, spec)
    assert ax.get_xscale() == scale
    plt.close(fig)


@pytest.mark.parametrize("scale", ["linear", "log"])
@matplotlib_available
def test_apply_common_style_yscale(scale: str) -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, yscale=scale)
    apply_common_style(ax, spec)
    assert ax.get_yscale() == scale
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_background_color() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, background_color="red")
    apply_common_style(ax, spec)
    assert ax.get_facecolor() == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_background_color() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10)
    default_facecolor = ax.get_facecolor()
    apply_common_style(ax, spec)
    assert ax.get_facecolor() == default_facecolor
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_ymin_ymax() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10, ymin=0.0, ymax=5.0)
    apply_common_style(ax, spec)
    assert ax.get_ylim() == (0.0, 5.0)
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_ymin_ymax() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(1, 101), bins=10)
    default_ylim = ax.get_ylim()
    apply_common_style(ax, spec)
    assert ax.get_ylim() == default_ylim
    plt.close(fig)


# --- xmin/xmax ---


@matplotlib_available
def test_apply_common_style_xmin_xmax() -> None:
    fig, ax = plt.subplots()
    # ``ScatterSpec`` rather than ``HistogramSpec``: ``HistogramSpec.xmin``/
    # ``.xmax`` is a different, quantile-capable field (see
    # ``plotmux.specs.base.XBoundSpec``), resolved and applied by
    # ``render_histogram`` itself, not the plain, explicit-value-only
    # ``BaseSpec``-shared ``xmin``/``xmax`` under test here.
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), xmin=0.0, xmax=5.0)
    apply_common_style(ax, spec)
    assert ax.get_xlim() == (0.0, 5.0)
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_xmin_xmax() -> None:
    fig, ax = plt.subplots()
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    default_xlim = ax.get_xlim()
    apply_common_style(ax, spec)
    assert ax.get_xlim() == default_xlim
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_histogram_xbounds_not_reapplied() -> None:
    # ``HistogramSpec``/``CdfSpec`` are not ``XBoundSpec`` (see
    # ``plotmux.specs.base.XBoundSpec``): their own ``xmin``/``xmax`` may
    # hold an unresolved quantile string, so ``apply_common_style`` must
    # not read them -- doing so used to crash the moment either bound was
    # set to a quantile string like ``"q0.1"``.
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, xmin="q0.1", xmax="q0.9")
    default_xlim = ax.get_xlim()
    apply_common_style(ax, spec)
    assert ax.get_xlim() == default_xlim
    plt.close(fig)


# --- legend_title ---


@matplotlib_available
def test_apply_common_style_legend_title() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_title="Lines")
    apply_common_style(ax, spec)
    assert ax.get_legend().get_title().get_text() == "Lines"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_legend_title() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_legend().get_title().get_text() == ""
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_legend_title_no_legend_is_noop() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_title="Lines")
    apply_common_style(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


# --- legend_location ---


@matplotlib_available
def test_apply_common_style_legend_location() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_location="top_left")
    apply_common_style(ax, spec)
    assert ax.get_legend()._get_loc() == 2  # "upper left"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_legend_location_best_passthrough() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_location="best")
    apply_common_style(ax, spec)
    assert ax.get_legend()._get_loc() == 0  # "best"
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_legend_location_no_legend_is_noop() -> None:
    fig, ax = plt.subplots()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_location="top_left")
    apply_common_style(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


# --- legend_orientation ---


@matplotlib_available
def test_apply_common_style_legend_orientation_horizontal() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s1")
    ax.plot([1, 2], [5, 6], label="s2")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10, legend_orientation="horizontal")
    apply_common_style(ax, spec)
    assert ax.get_legend()._ncols == 2
    plt.close(fig)


@matplotlib_available
def test_apply_common_style_no_legend_orientation() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4], label="s")
    ax.legend()
    spec = HistogramSpec(values=np.arange(101), bins=10)
    apply_common_style(ax, spec)
    assert ax.get_legend()._ncols == 1
    plt.close(fig)


#######################################
#     Tests for attach_repr_png     #
#######################################


@matplotlib_available
def test_attach_repr_png_adds_working_method() -> None:
    fig = MplFigure()
    fig.subplots().plot([1, 2, 3], [1, 4, 9])
    assert not hasattr(fig, "_repr_png_")
    attach_repr_png(fig)
    png = fig._repr_png_()
    assert isinstance(png, bytes)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


@matplotlib_available
def test_attach_repr_png_bare_figure_canvas_has_no_print_png() -> None:
    # Regression test: a ``Figure`` built via the constructor (rather than
    # ``pyplot.subplots()``) gets a plain ``FigureCanvasBase`` with no
    # ``print_png`` of its own -- this is exactly the gap ``attach_repr_png``
    # fixes (see its own docstring).
    fig = MplFigure()
    assert not hasattr(fig.canvas, "print_png")
