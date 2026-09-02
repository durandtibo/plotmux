from __future__ import annotations

import numpy as np

from plotmux.specs import LineSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.line import render_line

#################################
#     Tests for render_line     #
#################################


@altair_available
def test_render_line_returns_chart() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_line_label() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), label="my-label")
    chart = render_line(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "label"


@altair_available
def test_render_line_no_label_no_color_encoding() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    assert "color" not in chart.to_dict()["encoding"]


@altair_available
def test_render_line_no_color_uses_backend_default() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_line_color() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), color="red")
    chart = render_line(spec)
    assert chart.to_dict()["mark"]["color"] == "rgba(255, 0, 0, 1.0)"


@altair_available
def test_render_line_forwards_kwargs() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10))
    chart = render_line(spec, strokeWidth=5.0)
    assert chart.to_dict()["mark"]["strokeWidth"] == 5.0


@altair_available
def test_render_line_alpha() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), alpha=0.5)
    chart = render_line(spec)
    assert chart.to_dict()["mark"]["opacity"] == 0.5


@altair_available
def test_render_line_linewidth() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), linewidth=3.0)
    chart = render_line(spec)
    assert chart.to_dict()["mark"]["strokeWidth"] == 3.0


@altair_available
def test_render_line_linestyle() -> None:
    spec = LineSpec(x=np.arange(10), y=np.arange(10), linestyle="dashed")
    chart = render_line(spec)
    assert chart.to_dict()["mark"]["strokeDash"] is not None
