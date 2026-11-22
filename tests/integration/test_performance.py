r"""Performance gate of the core: the scene of large inputs is built in a
fraction of a second, and a line of 100,000 points renders on ``altair``
in well under the 3.4 s it took before its data became a CSV string.

The bounds are about 20 times the measured times, so the tests catch a
change of complexity and not the noise of a machine."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np
import pytest

import plotmux
from plotmux.scene import build_scene
from plotmux.specs import CdfSpec, HistogramSpec, PanelSpec
from plotmux.testing.fixtures import altair_available

if TYPE_CHECKING:
    from collections.abc import Callable

SCENE_SECONDS = 0.5
ALTAIR_LINE_SECONDS = 1.0


def elapsed(func: Callable[[], object]) -> float:
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


@pytest.fixture(scope="module")
def million() -> np.ndarray:
    return np.random.default_rng(0).normal(size=1_000_000)


@pytest.fixture(scope="module")
def hundred_thousand() -> np.ndarray:
    return np.random.default_rng(0).normal(size=100_000)


def test_build_scene_of_a_histogram_of_one_million_values_is_fast(million: np.ndarray) -> None:
    spec = PanelSpec(marks=(HistogramSpec(values=million),))
    assert elapsed(lambda: build_scene(spec)) < SCENE_SECONDS


def test_build_scene_of_an_exact_cdf_of_one_hundred_thousand_values_is_fast(
    hundred_thousand: np.ndarray,
) -> None:
    spec = PanelSpec(marks=(CdfSpec(values=hundred_thousand),))
    assert elapsed(lambda: build_scene(spec)) < SCENE_SECONDS


@altair_available
def test_altair_line_of_one_hundred_thousand_points_is_fast(hundred_thousand: np.ndarray) -> None:
    plotmux.line([0.0, 1.0], [0.0, 1.0], backend="altair")  # import the library first
    x = np.arange(100_000, dtype=float)
    assert (
        elapsed(lambda: plotmux.line(x, hundred_thousand, backend="altair")) < ALTAIR_LINE_SECONDS
    )
