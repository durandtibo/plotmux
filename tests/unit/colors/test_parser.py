from __future__ import annotations

from typing import Any

import pytest

from plotmux.colors import parse_color

################################
#     Tests for parse_color     #
################################


# --- hex strings ---


def test_parse_color_hex_rgb() -> None:
    assert parse_color("#ff0000") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_hex_rgba() -> None:
    assert parse_color("#ff000080") == pytest.approx((1.0, 0.0, 0.0, 128 / 255))


def test_parse_color_hex_black() -> None:
    assert parse_color("#000000") == (0.0, 0.0, 0.0, 1.0)


def test_parse_color_hex_uppercase() -> None:
    assert parse_color("#FF0000") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_hex_fully_transparent() -> None:
    assert parse_color("#ff000000") == (1.0, 0.0, 0.0, 0.0)


def test_parse_color_hex_lowercase() -> None:
    assert parse_color("#00ff00") == (0.0, 1.0, 0.0, 1.0)


def test_parse_color_hex_mixed_case() -> None:
    assert parse_color("#Ff00Aa") == pytest.approx((1.0, 0.0, 170 / 255, 1.0))


def test_parse_color_hex_rgba_uppercase() -> None:
    assert parse_color("#FF000080") == pytest.approx((1.0, 0.0, 0.0, 128 / 255))


def test_parse_color_hex_double_hash_prefix() -> None:
    # `lstrip("#")` strips every leading "#", not just one, so an
    # extra leading "#" is silently tolerated.
    assert parse_color("##ff0000") == (1.0, 0.0, 0.0, 1.0)


# --- named colors ---


def test_parse_color_named() -> None:
    assert parse_color("red") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_named_uppercase() -> None:
    assert parse_color("RED") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_named_mixed_case() -> None:
    assert parse_color("Tab:Blue") == parse_color("tab:blue")


def test_parse_color_named_base_shorthand() -> None:
    assert parse_color("k") == (0.0, 0.0, 0.0, 1.0)


def test_parse_color_matplotlib_named() -> None:
    r, g, b, a = parse_color("tab:blue")
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0
    assert a == 1.0


# --- RGB(A) tuples ---


def test_parse_color_rgb_tuple() -> None:
    assert parse_color((0.5, 0.5, 0.5)) == (0.5, 0.5, 0.5, 1.0)


def test_parse_color_rgba_tuple() -> None:
    assert parse_color((0.1, 0.2, 0.3, 0.4)) == (0.1, 0.2, 0.3, 0.4)


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        pytest.param((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), id="rgb_min_boundary"),
        pytest.param((1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), id="rgb_max_boundary"),
        pytest.param((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), id="rgba_min_boundary"),
        pytest.param((1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), id="rgba_max_boundary"),
    ],
)
def test_parse_color_tuple_boundary_values(
    color: tuple[float, ...], expected: tuple[float, float, float, float]
) -> None:
    assert parse_color(color) == expected  # type: ignore[arg-type]


def test_parse_color_tuple_returns_floats() -> None:
    r, g, b, a = parse_color((0, 0, 0))
    assert isinstance(r, float)
    assert isinstance(g, float)
    assert isinstance(b, float)
    assert isinstance(a, float)


# --- error cases ---


def test_parse_color_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color(123)  # type: ignore[arg-type]


def test_parse_color_invalid_type_none() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color(None)  # type: ignore[arg-type]


def test_parse_color_invalid_type_list() -> None:
    # A list is not accepted even though it behaves like a tuple.
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color([1.0, 0.0, 0.0])  # type: ignore[arg-type]


def test_parse_color_invalid_hex_length() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#fff")


def test_parse_color_invalid_hex_length_seven() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#ffff000")


def test_parse_color_invalid_hex_length_single_hash() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#")


def test_parse_color_invalid_hex_chars() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#zzzzzz")


def test_parse_color_invalid_hex_alpha_chars() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#ff0000zz")


def test_parse_color_unknown_name() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color("not-a-color")


def test_parse_color_unknown_name_error_mentions_color() -> None:
    with pytest.raises(ValueError, match="not-a-color"):
        parse_color("not-a-color")


def test_parse_color_empty_string() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color("")


def test_parse_color_whitespace_name_not_stripped() -> None:
    # Named-color lookup does not strip surrounding whitespace.
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color(" red")


@pytest.mark.parametrize(
    "bad_tuple",
    [
        pytest.param((), id="empty_tuple"),
        pytest.param((1,), id="single_value"),
        pytest.param((1, 2), id="two_values"),
        pytest.param((1, 2, 3, 4, 5), id="five_values"),
    ],
)
def test_parse_color_invalid_tuple_length(bad_tuple: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="Invalid color tuple"):
        parse_color(bad_tuple)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad_tuple",
    [
        pytest.param((-0.1, 0.5, 0.5), id="r_below_range"),
        pytest.param((0.5, -0.1, 0.5), id="g_below_range"),
        pytest.param((0.5, 0.5, -0.1), id="b_below_range"),
        pytest.param((0.5, 0.5, 1.5), id="b_above_range"),
        pytest.param((0.5, 0.5, 0.5, 2.0), id="a_above_range"),
        pytest.param((0.5, 0.5, 0.5, -1.0), id="a_below_range"),
    ],
)
def test_parse_color_out_of_range(bad_tuple: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="must be in the range"):
        parse_color(bad_tuple)  # type: ignore[arg-type]
