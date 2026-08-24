r"""Contain predefined colors and a default categorical palette.

Every value here is already a ``parse_color``-normalized RGBA tuple of
floats in ``[0, 1]``, so callers and backends never need to re-parse
them (same "canonical input, one parser, reused everywhere" pattern as
``parse_color`` itself — see ``plotmux.colors.parser``).
"""

from __future__ import annotations

__all__ = [
    "DEFAULT_PALETTE",
    "PRIMARY",
    "SECONDARY",
    "TERTIARY",
]

from plotmux.colors.parser import parse_color

PRIMARY = parse_color("tab:blue")
SECONDARY = parse_color("tab:orange")
TERTIARY = parse_color("tab:green")

#: Default categorical palette, an ordered tuple of RGBA tuples used to
#: assign successive, visually-distinct colors to multiple series or
#: ``LayerSpec`` children that set no explicit ``color``.
DEFAULT_PALETTE: tuple[tuple[float, float, float, float], ...] = (
    PRIMARY,
    SECONDARY,
    TERTIARY,
    parse_color("tab:red"),
    parse_color("tab:purple"),
    parse_color("tab:brown"),
    parse_color("tab:pink"),
    parse_color("tab:gray"),
    parse_color("tab:olive"),
    parse_color("tab:cyan"),
)
