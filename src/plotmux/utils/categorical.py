r"""Contain a small helper to detect a categorical (string) x-axis."""

from __future__ import annotations

__all__ = ["is_categorical"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def is_categorical(x: np.ndarray) -> bool:
    r"""Indicate whether ``x`` holds string categories rather than
    numeric positions.

    Shared by ``BarSpec``/``StackedBarSpec`` and the backends whose
    renderer needs to special-case a categorical x-axis (bokeh's
    ``FactorRange``, altair's ``:N`` field type -- see
    ``plotmux.backends.bokeh.bar``/``plotmux.backends.altair.bar``):
    matplotlib and plotly accept a string ``x`` natively and need no
    such check, but bokeh/altair need to know up front, before a
    glyph/mark is built, whether ``x`` is categorical.

    Args:
        x: The array of bar positions to check.

    Returns:
        ``True`` if ``x``'s dtype kind is unicode (``"U"``) or
            bytes (``"S"``), ``False`` otherwise (e.g. a numeric
            dtype).

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils.categorical import is_categorical
        >>> is_categorical(np.array(["a", "b", "c"]))
        True
        >>> is_categorical(np.arange(3))
        False

        ```
    """
    return x.dtype.kind in "US"
