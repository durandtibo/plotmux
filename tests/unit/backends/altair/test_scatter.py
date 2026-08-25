from __future__ import annotations

import numpy as np

from plotmux.specs import ScatterSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.scatter import render_scatter

####################################
#     Tests for render_scatter     #
####################################


@altair_available
def test_render_scatter_returns_chart() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_scatter_label() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    chart = render_scatter(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "label"


@altair_available
def test_render_scatter_no_label_no_color_encoding() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert "color" not in chart.to_dict()["encoding"]


@altair_available
def test_render_scatter_no_color_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_scatter_color() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), color="red")
    chart = render_scatter(spec)
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_scatter_size() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=100.0)
    chart = render_scatter(spec)
    assert chart.to_dict()["mark"]["size"] == 100.0


@altair_available
def test_render_scatter_no_size_uses_backend_default() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10))
    chart = render_scatter(spec)
    assert "size" not in chart.to_dict()["mark"]


@altair_available
def test_render_scatter_explicit_size_kwarg_not_overridden() -> None:
    spec = ScatterSpec(x=np.arange(10), y=np.arange(10), size=10.0)
    # ``size`` passed explicitly as a kwarg takes precedence over ``spec.size``
    # (``kwargs.setdefault("size", spec.size)`` in ``render_scatter``).
    chart = render_scatter(spec, size=99.0)
    assert chart.to_dict()["mark"]["size"] == 99.0
