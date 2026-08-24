r"""Contain a backend-agnostic color parser and predefined colors.

``parse_color`` normalizes the color formats users already know (hex
strings, CSS/matplotlib named colors, RGB(A) float tuples) into one
canonical representation, an RGBA tuple of floats in ``[0, 1]``. Each
backend then converts that canonical tuple to whatever its native call
expects (see ``plotmux.backends.matplotlib.style`` and
``plotmux.backends.xy.style``).

``palette`` supplies a small set of predefined named colors and a
default categorical palette, each already a ``parse_color``-normalized
RGBA tuple, on top of that same parser.
"""

from __future__ import annotations

__all__ = [
    "DEFAULT_PALETTE",
    "PRIMARY",
    "SECONDARY",
    "TERTIARY",
    "parse_color",
]

from plotmux.colors.palette import DEFAULT_PALETTE, PRIMARY, SECONDARY, TERTIARY
from plotmux.colors.parser import parse_color
