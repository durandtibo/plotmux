r"""End-to-end display coverage: ``Figure.show`` and the rich display of a
chart, a layer and a grid on every backend, with no patching of plotmux or
of the plotting libraries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

import plotmux
from plotmux.testing.fixtures import (
    altair_available,
    bokeh_available,
    matplotlib_available,
    plotly_available,
    xy_available,
)
from plotmux.utils.imports import is_plotly_available

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from plotmux.figure import Figure

if is_plotly_available():
    import plotly.io as pio

BACKENDS = [
    pytest.param("matplotlib", marks=matplotlib_available),
    pytest.param("xy", marks=xy_available),
    pytest.param("bokeh", marks=bokeh_available),
    pytest.param("altair", marks=altair_available),
    pytest.param("plotly", marks=plotly_available),
]


def _chart(backend: str) -> Figure:
    x = np.arange(5.0)
    return plotmux.line(x, x, backend=backend)


def _layer(backend: str) -> Figure:
    x = np.arange(5.0)
    return plotmux.layer(
        plotmux.line(x, x, backend=backend), plotmux.scatter(x, x, backend=backend), backend=backend
    )


def _grid(backend: str) -> Figure:
    x = np.arange(5.0)
    return plotmux.grid(
        plotmux.line(x, x, backend=backend),
        plotmux.hist(x, backend=backend),
        ncols=2,
        backend=backend,
    )


FIGURES = [_chart, _layer, _grid]


@pytest.fixture(autouse=True)
def _display_without_a_window() -> Iterator[None]:
    # plotly shows through a renderer: ``json`` prints instead of starting a
    # server and waiting for a browser.
    if is_plotly_available():
        previous = pio.renderers.default
        pio.renderers.default = "json"
    yield
    if is_plotly_available():
        pio.renderers.default = previous


@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive")
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("make_figure", FIGURES)
def test_show_does_not_raise(backend: str, make_figure: Callable[[str], Figure]) -> None:
    make_figure(backend).show()


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("make_figure", FIGURES)
def test_rich_display_has_a_representation(
    backend: str, make_figure: Callable[[str], Figure]
) -> None:
    bundle = make_figure(backend)._repr_mimebundle_()
    assert bundle
