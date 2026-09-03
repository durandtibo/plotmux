from __future__ import annotations

import numpy as np

from plotmux.specs import BarSeries, StackedBarSpec
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    import altair as alt

    from plotmux.backends.altair.stacked_bar import render_stacked_bar

########################################
#     Tests for render_stacked_bar     #
########################################


@altair_available
def test_render_stacked_bar_returns_chart() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    chart = render_stacked_bar(spec)
    assert isinstance(chart, alt.Chart)


@altair_available
def test_render_stacked_bar_long_form_data_length() -> None:
    spec = StackedBarSpec(
        x=np.arange(5), series=(BarSeries(y=np.arange(5)), BarSeries(y=np.arange(5)))
    )
    chart = render_stacked_bar(spec)
    assert len(chart.to_dict()["data"]["values"]) == 10


@altair_available
def test_render_stacked_bar_color_field_is_series() -> None:
    spec = StackedBarSpec(
        x=np.arange(5),
        series=(BarSeries(y=np.arange(5), label="s1"), BarSeries(y=np.arange(5), label="s2")),
    )
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["encoding"]["color"]["field"] == "series"


@altair_available
def test_render_stacked_bar_color_domain_matches_labels() -> None:
    spec = StackedBarSpec(
        x=np.arange(5),
        series=(BarSeries(y=np.arange(5), label="s1"), BarSeries(y=np.arange(5), label="s2")),
    )
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["encoding"]["color"]["scale"]["domain"] == ["s1", "s2"]


@altair_available
def test_render_stacked_bar_no_label_no_legend() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["encoding"]["color"]["legend"] is None


@altair_available
def test_render_stacked_bar_categorical_x() -> None:
    spec = StackedBarSpec(
        x=np.array(["Apples", "Pears", "Nectarines"]), series=(BarSeries(y=np.array([2, 1, 4])),)
    )
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["encoding"]["x"]["type"] == "nominal"


@altair_available
def test_render_stacked_bar_numeric_x() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),))
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["encoding"]["x"]["type"] == "quantitative"


@altair_available
def test_render_stacked_bar_alpha() -> None:
    spec = StackedBarSpec(x=np.arange(5), series=(BarSeries(y=np.arange(5)),), alpha=0.5)
    chart = render_stacked_bar(spec)
    assert chart.to_dict()["mark"]["opacity"] == 0.5
