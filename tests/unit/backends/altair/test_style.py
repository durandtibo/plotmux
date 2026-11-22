from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.primitives import Line
from plotmux.scene import AxesScene, LegendStyle
from plotmux.testing.fixtures import altair_available
from plotmux.utils.imports import is_altair_available

if is_altair_available():
    from plotmux.backends.altair.style import (
        LEGEND_LOCATION,
        MARKER_STYLE,
        STROKE_DASH,
        _format_column,
        axis_encodings,
        inline_data,
        legend_color,
        rgba_to_altair,
    )

RED = (1.0, 0.0, 0.0, 1.0)


def _color(scene: AxesScene) -> Any:
    return legend_color(scene)


def _scene(**kwargs: Any) -> AxesScene:
    return AxesScene(primitives=(), **kwargs)


def _line(label: str | None = None, color: Any = RED) -> Line:
    return Line(x=np.arange(2.0), y=np.arange(2.0), label=label, color=color)


###################################
#     Tests for rgba_to_altair    #
###################################


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        pytest.param((1.0, 0.0, 0.0, 1.0), "rgba(255, 0, 0, 1.0)", id="opaque"),
        pytest.param((0.0, 0.0, 0.0, 0.0), "rgba(0, 0, 0, 0.0)", id="transparent"),
        pytest.param((0.5, 0.5, 0.5, 0.5), "rgba(128, 128, 128, 0.5)", id="rounding"),
    ],
)
@altair_available
def test_rgba_to_altair(color: tuple[float, ...], expected: str) -> None:
    assert rgba_to_altair(cast("Any", color)) == expected


####################################
#     Tests for _format_column     #
####################################


@altair_available
def test_format_column_float() -> None:
    assert _format_column(np.array([1.5, 2.0])) == ["1.5", "2.0"]


@altair_available
def test_format_column_integer_is_written_as_float() -> None:
    assert _format_column(np.array([1, 2])) == ["1.0", "2.0"]


@altair_available
def test_format_column_nan_is_an_empty_cell() -> None:
    assert _format_column(np.array([1.0, np.nan])) == ["1.0", ""]


@altair_available
def test_format_column_float_round_trips() -> None:
    value = 0.1 + 0.2
    assert float(_format_column(np.array([value]))[0]) == value


@altair_available
def test_format_column_large_float_round_trips() -> None:
    assert float(_format_column(np.array([1.2345678901234567e300]))[0]) == 1.2345678901234567e300


@altair_available
def test_format_column_strings() -> None:
    assert _format_column(np.array(["a", "b"])) == ["a", "b"]


@pytest.mark.parametrize("text", ["a,b", "line\nbreak", "cr\rhere"])
@altair_available
def test_format_column_quotes_the_special_characters(text: str) -> None:
    assert _format_column(np.array([text])) == [f'"{text}"']


@altair_available
def test_format_column_escapes_a_quote() -> None:
    assert _format_column(np.array(['a"b'])) == ['"a""b"']


@altair_available
def test_format_column_bytes() -> None:
    assert _format_column(np.array([b"a", b"b"])) == ["a", "b"]


@altair_available
def test_format_column_empty() -> None:
    assert _format_column(np.array([])) == []


##################################
#     Tests for inline_data      #
##################################


@altair_available
def test_inline_data_values() -> None:
    data = inline_data({"x": np.array([1.0, 2.0]), "y": np.array([3.0, np.nan])})
    assert data.values == "x,y\n1.0,3.0\n2.0,"


@altair_available
def test_inline_data_format() -> None:
    data = inline_data({"x": np.array([1.0]), "name": np.array(["a"])})
    assert data.format.to_dict() == {"parse": {"x": "number", "name": "string"}, "type": "csv"}


@altair_available
def test_inline_data_categories_that_look_like_numbers_stay_strings() -> None:
    assert inline_data({"x": np.array(["1", "2"])}).format.parse == {"x": "string"}


@altair_available
def test_inline_data_one_row() -> None:
    assert inline_data({"x": np.array([1.0])}).values == "x\n1.0"


@altair_available
def test_inline_data_does_not_change_the_columns() -> None:
    x = np.array([1.0, np.nan])
    inline_data({"x": x})
    assert np.isnan(x[1])


@altair_available
def test_inline_data_different_lengths_raise() -> None:
    with pytest.raises(ValueError, match="zip"):
        inline_data({"x": np.array([1.0, 2.0]), "y": np.array([1.0])})


###################################
#     Tests for legend_color      #
###################################


@altair_available
def test_legend_color_without_legend_is_none() -> None:
    assert legend_color(_scene()) is None


@altair_available
def test_legend_color_scale() -> None:
    scene = AxesScene(
        primitives=(_line("a"), _line(None), _line("b", (0.0, 0.0, 1.0, 1.0))),
        legend=LegendStyle(),
    )
    scale = _color(scene).to_dict()["scale"]
    assert scale == {
        "domain": ["a", "b"],
        "range": ["rgba(255, 0, 0, 1.0)", "rgba(0, 0, 255, 1.0)"],
    }


@altair_available
def test_legend_color_field() -> None:
    color = _color(AxesScene(primitives=(_line("a"),), legend=LegendStyle()))
    assert color.to_dict()["field"] == "label"


@altair_available
def test_legend_color_hides_the_default_title() -> None:
    color = _color(AxesScene(primitives=(_line("a"),), legend=LegendStyle()))
    assert color.to_dict()["legend"] == {"title": None}


@altair_available
def test_legend_color_title() -> None:
    color = _color(AxesScene(primitives=(_line("a"),), legend=LegendStyle(title="Lines")))
    assert color.to_dict()["legend"]["title"] == "Lines"


@pytest.mark.parametrize("location", sorted(LEGEND_LOCATION) if is_altair_available() else [])
@altair_available
def test_legend_color_location(location: str) -> None:
    scene = AxesScene(primitives=(_line("a"),), legend=LegendStyle(location=cast("Any", location)))
    assert _color(scene).to_dict()["legend"]["orient"] == LEGEND_LOCATION[location]


@pytest.mark.parametrize("orientation", ["vertical", "horizontal"])
@altair_available
def test_legend_color_orientation(orientation: str) -> None:
    scene = AxesScene(
        primitives=(_line("a"),), legend=LegendStyle(orientation=cast("Any", orientation))
    )
    assert _color(scene).to_dict()["legend"]["direction"] == orientation


###################################
#     Tests for axis_encodings    #
###################################


@altair_available
def test_axis_encodings_keys() -> None:
    assert sorted(axis_encodings(_scene())) == ["x", "y"]


@altair_available
def test_axis_encodings_x2_key() -> None:
    assert sorted(axis_encodings(_scene(), x2_field="x2")) == ["x", "x2", "y"]


@altair_available
def test_axis_encodings_whole_encoding() -> None:
    encodings = axis_encodings(_scene(xlabel="x", ylabel="y", xscale="log", yscale="log"))
    assert {k: v.to_dict() for k, v in encodings.items()} == {
        "x": {"field": "x", "scale": {"type": "log"}, "title": "x", "type": "quantitative"},
        "y": {
            "field": "y",
            "scale": {"type": "log"},
            "stack": None,
            "title": "y",
            "type": "quantitative",
        },
    }


@altair_available
def test_axis_encodings_no_label_hides_the_title() -> None:
    assert axis_encodings(_scene())["x"].to_dict()["title"] is None


@altair_available
def test_axis_encodings_limits() -> None:
    encodings = axis_encodings(_scene(xlim=(1.0, 2.0), ylim=(3.0, 4.0)))
    assert (encodings["x"].to_dict()["scale"], encodings["y"].to_dict()["scale"]) == (
        {"domainMax": 2.0, "domainMin": 1.0, "type": "linear"},
        {"domainMax": 4.0, "domainMin": 3.0, "type": "linear"},
    )


@altair_available
def test_axis_encodings_single_bound() -> None:
    encodings = axis_encodings(_scene(xlim=(None, 2.0)))
    assert encodings["x"].to_dict()["scale"] == {"domainMax": 2.0, "type": "linear"}


@altair_available
def test_axis_encodings_categorical_x_is_nominal_and_ordered() -> None:
    x = axis_encodings(_scene(categories=("b", "a"), xlabel="x"))["x"].to_dict()
    assert x == {"field": "x", "sort": ["b", "a"], "title": "x", "type": "nominal"}


@altair_available
def test_axis_encodings_categorical_x_has_no_x2() -> None:
    assert "x2" not in axis_encodings(_scene(categories=("a",)), x2_field="x2")


@altair_available
def test_axis_encodings_fields() -> None:
    encodings = axis_encodings(_scene(), x_field="x0", y_field="top")
    assert (encodings["x"].to_dict()["field"], encodings["y"].to_dict()["field"]) == ("x0", "top")


@altair_available
def test_tables() -> None:
    assert (STROKE_DASH["dashed"], MARKER_STYLE["x"]) == ([6, 4], "M-1,-1L1,1M-1,1L1,-1")
