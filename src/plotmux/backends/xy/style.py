r"""Contain xy-specific style helpers shared across chart types.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["rgba_to_xy"]


def rgba_to_xy(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to xy's native CSS color string.

    xy's mark color parameters accept a CSS color string (e.g.
    ``"rgba(255, 0, 0, 1)"``), so the canonical ``[0, 1]`` float RGBA
    tuple produced by ``plotmux.core.color.parse_color`` is converted
    to that format here rather than in ``core/``, keeping ``core/``
    free of any single backend's native color representation.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a CSS ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a``
            as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.xy.style import rgba_to_xy
        >>> rgba_to_xy((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"
