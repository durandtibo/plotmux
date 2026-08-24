from __future__ import annotations

import numpy as np
import pytest

import plotmux
from plotmux.testing.fixtures import matplotlib_available, xy_available


@matplotlib_available
def test_hist_returns_figure_with_matplotlib_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10)
    assert fig.backend_name == "matplotlib"
    assert fig.spec.bins == 10


@matplotlib_available
def test_hist_explicit_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10, backend="matplotlib")
    assert fig.backend_name == "matplotlib"


@xy_available
def test_hist_explicit_xy_backend() -> None:
    fig = plotmux.hist(np.arange(101), bins=10, backend="xy")
    assert fig.backend_name == "xy"
    assert fig.spec.bins == 10


def test_hist_unknown_backend_raises() -> None:
    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.hist(np.arange(101), backend="does-not-exist")
