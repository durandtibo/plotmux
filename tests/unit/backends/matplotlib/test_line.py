from __future__ import annotations

import numpy as np

from plotmux.specs import LineSpec
from plotmux.testing.fixtures import matplotlib_available
from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    import matplotlib.pyplot as plt

    from plotmux.backends.matplotlib.line import render_line


@matplotlib_available
def test_render_line_returns_axes() -> None:
    fig, ax = plt.subplots()
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    out = render_line(ax, spec)
    assert out is ax
    plt.close(fig)


@matplotlib_available
def test_render_line_draws_one_line() -> None:
    fig, ax = plt.subplots()
    spec = LineSpec(x=np.arange(10), y=np.arange(10) ** 2)
    render_line(ax, spec)
    assert len(ax.lines) == 1
    plt.close(fig)


@matplotlib_available
def test_render_line_label_adds_legend() -> None:
    fig, ax = plt.subplots()
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    render_line(ax, spec)
    assert ax.get_legend() is not None
    plt.close(fig)


@matplotlib_available
def test_render_line_no_label_no_legend() -> None:
    fig, ax = plt.subplots()
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    render_line(ax, spec)
    assert ax.get_legend() is None
    plt.close(fig)


@matplotlib_available
def test_render_line_color() -> None:
    fig, ax = plt.subplots()
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    render_line(ax, spec)
    assert ax.lines[0].get_color() == (1.0, 0.0, 0.0, 1.0)
    plt.close(fig)
