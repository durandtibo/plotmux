r"""Contain the altair helpers: the translation tables, the inline data
and the encodings of an ``AxesScene``.

This module is only imported when altair is installed (see
``plotmux.backends.altair.__init__``), so it can import altair
unconditionally.
"""

from __future__ import annotations

__all__ = [
    "LEGEND_LOCATION",
    "MARKER_STYLE",
    "STROKE_DASH",
    "axis_encodings",
    "inline_data",
    "legend_color",
    "rgba_to_altair",
]

import math
from typing import TYPE_CHECKING, Any, cast

import altair as alt

if TYPE_CHECKING:
    from collections.abc import Mapping

    import numpy as np

    from plotmux.scene import AxesScene

#: The Vega-Lite ``strokeDash`` of each portable line style (a solid line
#: has none).
STROKE_DASH = {"dashed": [6, 4], "dotted": [1, 3], "dashdot": [6, 4, 1, 4]}

#: The Vega-Lite ``shape`` of each portable marker name. The cross ``x``
#: is a custom SVG path: Vega-Lite has no named shape for it.
MARKER_STYLE = {
    "circle": "circle",
    "square": "square",
    "triangle": "triangle-up",
    "diamond": "diamond",
    "cross": "cross",
    "x": "M-1,-1L1,1M-1,1L1,-1",
}

#: The Vega-Lite legend ``orient`` of each portable legend location.
LEGEND_LOCATION = {
    "top_left": "top-left",
    "top_right": "top-right",
    "bottom_left": "bottom-left",
    "bottom_right": "bottom-right",
    "top": "top",
    "bottom": "bottom",
    "left": "left",
    "right": "right",
}


def rgba_to_altair(color: tuple[float, float, float, float]) -> str:
    r"""Convert a canonical RGBA tuple to altair's native color string.

    Args:
        color: The color as an ``(r, g, b, a)`` tuple of floats in
            ``[0, 1]``.

    Returns:
        The color as a CSS ``"rgba(r, g, b, a)"`` string, with
            ``r``/``g``/``b`` as integers in ``[0, 255]`` and ``a``
            as a float in ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.style import rgba_to_altair
        >>> rgba_to_altair((1.0, 0.0, 0.0, 1.0))
        'rgba(255, 0, 0, 1.0)'

        ```
    """
    r, g, b, a = color
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a})"


def _format_column(values: np.ndarray) -> list[str]:
    r"""Format a column as the cells of a CSV file.

    Args:
        values: The column. A string column is quoted when needed, a
            numeric column is written with ``repr`` (so it round-trips)
            and ``NaN`` is an empty cell.

    Returns:
        One string per value.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.style import _format_column
        >>> _format_column(np.array([1.5, np.nan]))
        ['1.5', '']
        >>> _format_column(np.array(["a,b", "c"]))
        ['"a,b"', 'c']

        ```
    """
    if values.dtype.kind in "US":
        cells = values.astype(str).tolist()
        return [
            '"' + cell.replace('"', '""') + '"' if any(c in cell for c in ',"\n\r') else cell
            for cell in cells
        ]
    return ["" if math.isnan(value) else repr(value) for value in values.astype(float).tolist()]


def inline_data(columns: Mapping[str, np.ndarray]) -> alt.InlineData:
    r"""Build the inline data of a chart from columns.

    The data is one CSV string with an explicit ``parse`` of each
    column. altair validates a list of records against the Vega-Lite
    schema row by row, which takes seconds for 100,000 points, and a
    string is validated in constant time.

    Args:
        columns: The columns, by field name. All have the same length.

    Returns:
        The ``InlineData`` holding the CSV text.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.backends.altair.style import inline_data
        >>> data = inline_data({"x": np.array([1.0, 2.0]), "label": np.array(["a", "a"])})
        >>> data.values
        'x,label\n1.0,a\n2.0,a'
        >>> data.format.parse
        {'x': 'number', 'label': 'string'}

        ```
    """
    cells = [_format_column(column) for column in columns.values()]
    lines = [",".join(columns), *(",".join(row) for row in zip(*cells, strict=True))]
    parse = {
        name: "string" if column.dtype.kind in "US" else "number"
        for name, column in columns.items()
    }
    return alt.InlineData(
        values="\n".join(lines),
        format=alt.CsvDataFormat(type="csv", parse=parse),
    )


def legend_color(scene: AxesScene) -> alt.Color | None:
    r"""Build the ``color`` encoding that draws the legend of a scene.

    A legend entry exists only for a field-based color encoding, so the
    labeled primitives carry a constant ``"label"`` field bound to one
    scale of the whole axes: its domain is the labels and its range is
    their colors. Every layer uses the same encoding, so Vega-Lite merges
    them into one legend.

    Args:
        scene: The scene whose labeled primitives to list.

    Returns:
        The ``color`` encoding, or ``None`` if the scene has no legend.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.style import legend_color
        >>> from plotmux.scene import AxesScene
        >>> legend_color(AxesScene(primitives=())) is None
        True

        ```
    """
    if scene.legend is None:
        return None
    entries = {
        p.label: rgba_to_altair(p.color)
        for p in scene.primitives
        if p.label is not None and p.color is not None
    }
    legend: dict[str, Any] = {"title": scene.legend.title}
    if scene.legend.location is not None:
        legend["orient"] = LEGEND_LOCATION[scene.legend.location]
    if scene.legend.orientation is not None:
        legend["direction"] = scene.legend.orientation
    return alt.Color(
        "label:N",
        scale=alt.Scale(domain=list(entries), range=list(entries.values())),
        legend=alt.Legend(**cast("Any", legend)),
    )


def axis_encodings(
    scene: AxesScene, *, x_field: str = "x", y_field: str = "y", x2_field: str | None = None
) -> dict[str, Any]:
    r"""Build the ``x`` and ``y`` encodings of the axes of a scene.

    The title, the scale and the limits are the same for every layer of
    the axes, so Vega-Lite merges the axes. A ``None`` label is passed
    explicitly: it hides the axis title, while omitting it would show
    the name of the field.

    Args:
        scene: The scene whose axes to encode.
        x_field: The field of the x channel.
        y_field: The field of the y channel.
        x2_field: The field of the ``x2`` channel of a bar over an
            interval, or ``None``.

    Returns:
        The keyword arguments of ``Chart.encode``. A categorical x-axis
            is nominal and ordered like ``scene.categories``.

    Example:
        ```pycon
        >>> from plotmux.backends.altair.style import axis_encodings
        >>> from plotmux.scene import AxesScene
        >>> sorted(axis_encodings(AxesScene(primitives=())))
        ['x', 'y']

        ```
    """
    y_scale: dict[str, Any] = {"type": scene.yscale}
    if scene.ylim[0] is not None:
        y_scale["domainMin"] = scene.ylim[0]
    if scene.ylim[1] is not None:
        y_scale["domainMax"] = scene.ylim[1]
    encodings: dict[str, Any] = {
        "y": alt.Y(f"{y_field}:Q", title=scene.ylabel, scale=alt.Scale(**y_scale), stack=None)
    }
    if scene.categories is not None:
        encodings["x"] = alt.X(f"{x_field}:N", title=scene.xlabel, sort=list(scene.categories))
        return encodings
    x_scale: dict[str, Any] = {"type": scene.xscale}
    if scene.xlim[0] is not None:
        x_scale["domainMin"] = scene.xlim[0]
    if scene.xlim[1] is not None:
        x_scale["domainMax"] = scene.xlim[1]
    encodings["x"] = alt.X(f"{x_field}:Q", title=scene.xlabel, scale=alt.Scale(**x_scale))
    if x2_field is not None:
        encodings["x2"] = alt.X2(f"{x2_field}:Q")
    return encodings
