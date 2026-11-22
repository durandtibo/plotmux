r"""End-to-end coverage of the input policy of ``NaN`` and ``inf`` (see
``plotmux.utils.finite``) through the public API on every backend."""

from __future__ import annotations

import numpy as np
import pytest

import plotmux
from plotmux.exceptions import InvalidSpecError
from plotmux.testing.fixtures import (
    altair_available,
    bokeh_available,
    matplotlib_available,
    plotly_available,
    xy_available,
)

BACKENDS = [
    pytest.param("matplotlib", marks=matplotlib_available),
    pytest.param("xy", marks=xy_available),
    pytest.param("bokeh", marks=bokeh_available),
    pytest.param("altair", marks=altair_available),
    pytest.param("plotly", marks=plotly_available),
]

VALUES = [1.0, 2.0, np.nan, 3.0, np.inf, 4.0]


@pytest.mark.parametrize("backend", BACKENDS)
def test_hist_with_non_finite_values_renders(backend: str) -> None:
    with pytest.warns(UserWarning, match=r"2 non-finite value\(s\)"):
        fig = plotmux.hist(VALUES, bins=4, backend=backend)
    assert fig.native is not None


@pytest.mark.parametrize("backend", BACKENDS)
def test_hist_with_non_finite_values_and_quantile_range_renders(backend: str) -> None:
    with pytest.warns(UserWarning, match=r"2 non-finite value\(s\)"):
        fig = plotmux.hist(VALUES, bins=4, xmin="q0.0", xmax="q1.0", backend=backend)
    assert fig.native is not None


@pytest.mark.parametrize("backend", BACKENDS)
def test_cdf_with_non_finite_values_renders(backend: str) -> None:
    with pytest.warns(UserWarning, match=r"2 non-finite value\(s\)"):
        fig = plotmux.cdf(VALUES, nbins=4, backend=backend)
    assert fig.native is not None


@pytest.mark.parametrize("backend", BACKENDS)
def test_line_with_nan_renders(backend: str) -> None:
    fig = plotmux.line([0.0, 1.0, 2.0], [1.0, np.nan, 3.0], backend=backend)
    assert fig.native is not None


@pytest.mark.parametrize("backend", BACKENDS)
def test_scatter_with_nan_renders(backend: str) -> None:
    fig = plotmux.scatter([0.0, 1.0, 2.0], [1.0, np.nan, 3.0], backend=backend)
    assert fig.native is not None


@pytest.mark.parametrize("backend", BACKENDS)
def test_line_with_inf_raises_whatever_the_backend(backend: str) -> None:
    with pytest.raises(InvalidSpecError, match="LineSpec: y must not contain inf"):
        plotmux.line([0.0, 1.0, 2.0], [1.0, np.inf, 3.0], backend=backend)


@pytest.mark.parametrize("backend", BACKENDS)
def test_scatter_with_inf_raises_whatever_the_backend(backend: str) -> None:
    with pytest.raises(InvalidSpecError, match="ScatterSpec: x must not contain inf"):
        plotmux.scatter([0.0, -np.inf, 2.0], [1.0, 2.0, 3.0], backend=backend)
