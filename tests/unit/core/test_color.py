from __future__ import annotations

import pytest

from plotmux.core.color import parse_color


def test_parse_color_hex_rgb() -> None:
    assert parse_color("#ff0000") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_hex_rgba() -> None:
    assert parse_color("#ff000080") == pytest.approx((1.0, 0.0, 0.0, 128 / 255))


def test_parse_color_named() -> None:
    assert parse_color("red") == (1.0, 0.0, 0.0, 1.0)


def test_parse_color_matplotlib_named() -> None:
    r, g, b, a = parse_color("tab:blue")
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0
    assert a == 1.0


def test_parse_color_rgb_tuple() -> None:
    assert parse_color((0.5, 0.5, 0.5)) == (0.5, 0.5, 0.5, 1.0)


def test_parse_color_rgba_tuple() -> None:
    assert parse_color((0.1, 0.2, 0.3, 0.4)) == (0.1, 0.2, 0.3, 0.4)


def test_parse_color_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color(123)  # type: ignore[arg-type]


def test_parse_color_invalid_hex_length() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#fff")


def test_parse_color_invalid_hex_chars() -> None:
    with pytest.raises(ValueError, match="Invalid hex color"):
        parse_color("#zzzzzz")


def test_parse_color_unknown_name() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color("not-a-color")


@pytest.mark.parametrize("bad_tuple", [(1, 2), (1, 2, 3, 4, 5)])
def test_parse_color_invalid_tuple_length(bad_tuple: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="Invalid color tuple"):
        parse_color(bad_tuple)


@pytest.mark.parametrize("bad_tuple", [(-0.1, 0.5, 0.5), (0.5, 0.5, 1.5), (0.5, 0.5, 0.5, 2.0)])
def test_parse_color_out_of_range(bad_tuple: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="must be in the range"):
        parse_color(bad_tuple)
