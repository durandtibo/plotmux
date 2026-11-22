r"""Check the property "same chart everywhere".

For each mark, each context (standalone, in a layer, in a grid) and
each backend, nothing raises and what the native figure draws equals
the primitives of ``build_scene``. It is the support matrix of the
design, executable.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from plotmux.backends.registry import get_backend
from plotmux.scene import GridScene, build_scene
from plotmux.specs import (
    BarSeries,
    BarSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LineSpec,
    PanelSpec,
    ScatterSpec,
    SlopeSpec,
    StackedBarSpec,
)
from plotmux.testing.fixtures import matplotlib_available, xy_available
from tests.integration.conformance.extract import (
    Drawn,
    expected,
    extract_matplotlib,
    extract_xy,
)

RNG = np.random.default_rng(0)
VALUES = RNG.normal(size=200)
X = np.arange(6.0)
Y = X**2
CATEGORIES = np.array(["a", "b", "c"])

# Each mark with its kind of x, and a sibling of the same kind for a layer.
MARKS: dict[str, Any] = {
    "hist": HistogramSpec(values=VALUES, bins=12, label="hist"),
    "cdf": CdfSpec(values=VALUES, label="cdf"),
    "cdf_binned": CdfSpec(values=VALUES, nbins=10),
    "bar": BarSpec(x=X, y=Y, width=0.5, label="bar"),
    "bar_categorical": BarSpec(x=CATEGORIES, y=np.array([3.0, 1.0, 2.0]), label="bar"),
    "stacked_bar": StackedBarSpec(
        x=X,
        series=(BarSeries(y=Y, label="s0"), BarSeries(y=Y[::-1], label="s1")),
        width=0.5,
    ),
    "stacked_bar_categorical": StackedBarSpec(
        x=CATEGORIES,
        series=(BarSeries(y=np.array([3.0, 1.0, 2.0])), BarSeries(y=np.array([1.0, 1.0, 1.0]))),
    ),
    "line": LineSpec(x=X, y=Y, label="line"),
    "scatter": ScatterSpec(x=X, y=Y, label="scatter"),
    "slope": SlopeSpec(gradient=2.0, intercept=1.0, label="slope"),
}
CATEGORICAL = {"bar_categorical", "stacked_bar_categorical"}
SIBLING_NUMERIC = LineSpec(x=np.array([0.0, 10.0]), y=np.array([0.0, 5.0]))
SIBLING_CATEGORICAL = BarSpec(x=CATEGORIES, y=np.array([1.0, 2.0, 3.0]))


def _panel(name: str, *, layer: bool) -> PanelSpec:
    mark = MARKS[name]
    if name == "slope" and not layer:
        return PanelSpec(marks=(mark,), xmin=0, xmax=10)
    if not layer:
        return PanelSpec(marks=(mark,))
    sibling = SIBLING_CATEGORICAL if name in CATEGORICAL else SIBLING_NUMERIC
    return PanelSpec(marks=(sibling, mark))


def _spec(name: str, context: str) -> PanelSpec | GridSpec:
    if context == "standalone":
        return _panel(name, layer=False)
    if context == "layer":
        return _panel(name, layer=True)
    return GridSpec(panels=(_panel(name, layer=False), _panel(name, layer=True)), ncols=2)


def _axes_matplotlib(native: Any) -> list[Drawn]:
    return [extract_matplotlib(ax) for ax in native.axes if ax.get_visible()]


def _axes_xy(native: Any) -> list[Drawn]:
    charts = native.charts if hasattr(native, "charts") else [native]
    return [extract_xy(chart) for chart in charts]


BACKENDS = [
    pytest.param("matplotlib", _axes_matplotlib, marks=matplotlib_available),
    pytest.param("xy", _axes_xy, marks=xy_available),
]


def _scenes(spec: PanelSpec | GridSpec) -> list[Any]:
    scene = build_scene(spec)
    return list(scene.panels) if isinstance(scene, GridScene) else [scene]


def _check_group(actual: list[tuple[Any, ...]], wanted: list[tuple[Any, ...]]) -> None:
    assert len(actual) == len(wanted)
    for got, want in zip(actual, wanted, strict=True):
        for a, w in zip(got, want, strict=True):
            if w is None or isinstance(w, tuple):
                assert a == pytest.approx(w) if w is not None else a is None
            elif np.asarray(w).dtype.kind in "US":
                assert np.asarray(a).astype(str).tolist() == np.asarray(w).astype(str).tolist()
            else:
                np.testing.assert_allclose(np.asarray(a, dtype=float), w, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("context", ["standalone", "layer", "grid"])
@pytest.mark.parametrize("name", list(MARKS))
@pytest.mark.parametrize(("backend_name", "axes"), BACKENDS)
def test_backend_draws_the_primitives_of_the_scene(
    backend_name: str, axes: Any, name: str, context: str
) -> None:
    spec = _spec(name, context)
    native = get_backend(backend_name).render(spec)
    drawn = axes(native)
    scenes = _scenes(spec)
    assert len(drawn) == len(scenes)
    for panel_drawn, scene in zip(drawn, scenes, strict=True):
        wanted = expected(scene)
        _check_group(panel_drawn.bars, wanted.bars)
        _check_group(_comparable(panel_drawn.lines, wanted.lines), wanted.lines)
        _check_group(panel_drawn.points, wanted.points)


def _comparable(
    actual: list[tuple[Any, ...]], wanted: list[tuple[Any, ...]]
) -> list[tuple[Any, ...]]:
    r"""Compare a native infinite line by its slope and intercept, and the
    other lines by their vertices: a backend without a native infinite
    line draws the segment."""
    result = []
    for got, want in zip(actual, wanted, strict=True):
        if want[2] is not None and got[2] is None:
            result.append((got[0], got[1], want[2]))
        elif want[2] is not None:
            result.append((want[0], want[1], got[2]))
        else:
            result.append(got)
    return result
