from __future__ import annotations

from plotmux.colors import DEFAULT_PALETTE, PRIMARY, SECONDARY, TERTIARY
from plotmux.colors.parser import parse_color


def test_default_palette_is_nonempty() -> None:
    assert len(DEFAULT_PALETTE) > 0


def test_default_palette_entries_are_valid_rgba_tuples() -> None:
    for color in DEFAULT_PALETTE:
        assert len(color) == 4
        assert all(0.0 <= value <= 1.0 for value in color)


def test_default_palette_starts_with_primary_secondary_tertiary() -> None:
    assert DEFAULT_PALETTE[:3] == (PRIMARY, SECONDARY, TERTIARY)


def test_primary_is_already_parsed() -> None:
    assert parse_color("tab:blue") == PRIMARY
