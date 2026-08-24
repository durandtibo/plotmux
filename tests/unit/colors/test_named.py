from __future__ import annotations

import pytest

from plotmux.colors.named import NAMED_COLORS

################################
#     Tests for NAMED_COLORS     #
################################


def test_named_colors_is_nonempty() -> None:
    assert len(NAMED_COLORS) > 0


def test_named_colors_entries_are_rgba_tuples_in_unit_range() -> None:
    for color in NAMED_COLORS.values():
        assert len(color) == 4
        assert all(0.0 <= value <= 1.0 for value in color)


def test_named_colors_entries_are_float_tuples() -> None:
    for color in NAMED_COLORS.values():
        assert all(isinstance(value, float) for value in color)


def test_named_colors_names_are_lowercase() -> None:
    assert all(name == name.lower() for name in NAMED_COLORS)


def test_named_colors_fully_opaque() -> None:
    assert all(color[3] == 1.0 for color in NAMED_COLORS.values())


def test_named_colors_contains_base_colors() -> None:
    for name in ("b", "g", "r", "c", "m", "y", "k", "w"):
        assert name in NAMED_COLORS


def test_named_colors_base_color_values() -> None:
    assert NAMED_COLORS["r"] == (1.0, 0.0, 0.0, 1.0)
    assert NAMED_COLORS["k"] == (0.0, 0.0, 0.0, 1.0)
    assert NAMED_COLORS["w"] == (1.0, 1.0, 1.0, 1.0)


def test_named_colors_contains_tableau_colors() -> None:
    for name in (
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
        "tab:purple",
        "tab:brown",
        "tab:pink",
        "tab:gray",
        "tab:olive",
        "tab:cyan",
    ):
        assert name in NAMED_COLORS


def test_named_colors_tab_blue_value() -> None:
    assert NAMED_COLORS["tab:blue"] == pytest.approx((0x1F / 255, 0x77 / 255, 0xB4 / 255, 1.0))


def test_named_colors_contains_css4_colors() -> None:
    for name in ("red", "green", "blue", "black", "white", "crimson", "rebeccapurple"):
        assert name in NAMED_COLORS


def test_named_colors_css4_color_values() -> None:
    assert NAMED_COLORS["red"] == (1.0, 0.0, 0.0, 1.0)
    assert NAMED_COLORS["black"] == (0.0, 0.0, 0.0, 1.0)
    assert NAMED_COLORS["white"] == (1.0, 1.0, 1.0, 1.0)


def test_named_colors_unknown_name_is_absent() -> None:
    assert "not-a-color" not in NAMED_COLORS
