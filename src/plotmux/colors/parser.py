r"""Contain a backend-agnostic color parser.

``parse_color`` normalizes the color formats users already know (hex
strings, CSS/matplotlib named colors, RGB(A) float tuples) into one
canonical representation, an RGBA tuple of floats in ``[0, 1]``. Each
backend then converts that canonical tuple to whatever its native call
expects (see ``plotmux.backends.matplotlib.style`` and
``plotmux.backends.xy.style``).
"""

from __future__ import annotations

__all__ = ["parse_color"]

from plotmux.colors.named import NAMED_COLORS


def parse_color(
    color: str | tuple[float, float, float] | tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    r"""Parse a color into a canonical RGBA tuple of floats in ``[0,
    1]``.

    Args:
        color: The color to parse. It can be a hex string
            (``"#rrggbb"`` or ``"#rrggbbaa"``), a CSS/matplotlib
            named color (e.g. ``"tab:blue"``, ``"crimson"``), or an
            RGB(A) tuple of floats in ``[0, 1]``.

    Returns:
        The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Raises:
        ValueError: if ``color`` is not a valid color.

    Example:
        ```pycon
        >>> from plotmux.colors import parse_color
        >>> parse_color("#ff0000")
        (1.0, 0.0, 0.0, 1.0)
        >>> parse_color((0.5, 0.5, 0.5))
        (0.5, 0.5, 0.5, 1.0)

        ```
    """
    if isinstance(color, str):
        return _parse_str(color)
    if isinstance(color, tuple):
        return _parse_tuple(color)
    msg = f"Invalid color {color!r}: expected a str or a tuple of floats"
    raise ValueError(msg)


def _parse_str(color: str) -> tuple[float, float, float, float]:
    if color.startswith("#"):
        return _parse_hex(color)
    # Named colors (CSS4 and matplotlib's own "tab:blue"-style names) are
    # validated against a static color table bundled with plotmux (see
    # ``plotmux.colors.named``), mirroring matplotlib's own color tables.
    # This works whether or not matplotlib is installed.
    try:
        return NAMED_COLORS[color.lower()]
    except KeyError as err:
        msg = f"Invalid color {color!r}: unknown named color or malformed hex string"
        raise ValueError(msg) from err


def _parse_hex(value: str) -> tuple[float, float, float, float]:
    hex_str = value.lstrip("#")
    if len(hex_str) not in (6, 8):
        msg = f"Invalid hex color {value!r}: expected '#rrggbb' or '#rrggbbaa'"
        raise ValueError(msg)
    try:
        r, g, b = (int(hex_str[i : i + 2], 16) / 255 for i in (0, 2, 4))
        a = int(hex_str[6:8], 16) / 255 if len(hex_str) == 8 else 1.0
    except ValueError as err:
        msg = f"Invalid hex color {value!r}: not a valid hexadecimal string"
        raise ValueError(msg) from err
    return (r, g, b, a)


def _parse_tuple(color: tuple[float, ...]) -> tuple[float, float, float, float]:
    if len(color) == 3:
        r, g, b = color
        a = 1.0
    elif len(color) == 4:
        r, g, b, a = color
    else:
        msg = f"Invalid color tuple {color!r}: expected 3 or 4 floats"
        raise ValueError(msg)
    names = ("r", "g", "b", "a")
    values = (r, g, b, a)
    for name, value in zip(names, values, strict=True):
        if not 0.0 <= value <= 1.0:
            msg = (
                f"Invalid color tuple {color!r}: component {name!r}={value!r} "
                "must be in the range [0, 1]"
            )
            raise ValueError(msg)
    return (float(r), float(g), float(b), float(a))
