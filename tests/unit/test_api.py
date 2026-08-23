from __future__ import annotations

import numpy as np
import pytest

from plotmux.testing.fixtures import matplotlib_available


@matplotlib_available
def test_hist_returns_figure_with_matplotlib_backend() -> None:
    import plotmux

    fig = plotmux.hist(np.arange(101), bins=10)
    assert fig.backend_name == "matplotlib"
    assert fig.spec.bins == 10


@matplotlib_available
def test_hist_explicit_backend() -> None:
    import plotmux

    fig = plotmux.hist(np.arange(101), bins=10, backend="matplotlib")
    assert fig.backend_name == "matplotlib"


def test_hist_unknown_backend_raises() -> None:
    import plotmux

    with pytest.raises(RuntimeError, match="No backend registered"):
        plotmux.hist(np.arange(101), backend="does-not-exist")
