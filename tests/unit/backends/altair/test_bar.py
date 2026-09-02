from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.bar import render_bar

################################
#     Tests for render_bar     #
################################


@altair_available
def test_render_bar_returns_chart() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    chart = render_bar(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_bar_label() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), label="my-label")
    chart = render_bar(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "label"


@altair_available
def test_render_bar_no_label_no_color_encoding() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    chart = render_bar(spec)
    assert "color" not in chart.to_dict()["encoding"]


@altair_available
def test_render_bar_no_color_uses_backend_default() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5))
    chart = render_bar(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_bar_color() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), color="red")
    chart = render_bar(spec)
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_bar_alpha() -> None:
    spec = BarSpec(x=np.arange(5), y=np.arange(5), alpha=0.5)
    chart = render_bar(spec)
    assert chart.to_dict()["mark"]["opacity"] == 0.5
