r"""Read the primitives back from a native figure.

``extract_<backend>(native)`` returns the primitives a native figure
draws, so the conformance test can check that every backend draws the
same numbers as ``plotmux.scene.build_scene``.
"""

from __future__ import annotations

__all__ = [
    "Drawn",
    "expected",
    "extract_altair",
    "extract_bokeh",
    "extract_matplotlib",
    "extract_plotly",
    "extract_xy",
]

import csv
import io
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from plotmux.primitives import Bars, Line, Points

if TYPE_CHECKING:
    from plotmux.scene import AxesScene


@dataclass
class Drawn:
    r"""Hold the primitives drawn by one axes, grouped by kind.

    Each bars entry is ``(x, height, base, width)``, each line entry is
    ``(x, y, infinite)`` (``x`` and ``y`` are ``None`` for a native
    infinite line) and each points entry is ``(x, y)``.
    """

    bars: list[tuple[Any, ...]] = field(default_factory=list)
    lines: list[tuple[Any, ...]] = field(default_factory=list)
    points: list[tuple[Any, ...]] = field(default_factory=list)


def expected(scene: AxesScene) -> Drawn:
    r"""Return the primitives of a scene in the shape of ``Drawn``."""
    drawn = Drawn()
    for primitive in scene.primitives:
        if isinstance(primitive, Bars):
            n = primitive.x.shape[0]
            drawn.bars.append(
                (
                    primitive.x,
                    primitive.height,
                    primitive.base,
                    np.broadcast_to(np.asarray(primitive.width, dtype=float), (n,)),
                )
            )
        elif isinstance(primitive, Line):
            drawn.lines.append((primitive.x, primitive.y, primitive.infinite))
        elif isinstance(primitive, Points):
            drawn.points.append((primitive.x, primitive.y))
    return drawn


def extract_matplotlib(ax: Any) -> Drawn:
    r"""Read the primitives drawn on a matplotlib ``Axes``."""
    drawn = Drawn()
    categories = {}
    units = ax.xaxis.get_units()
    if units is not None and hasattr(units, "_mapping"):
        categories = {index: name for name, index in units._mapping.items()}
    for container in ax.containers:
        patches = container.patches
        x = np.array([p.get_x() + p.get_width() / 2 for p in patches])
        if categories:
            x = np.array([categories[round(v)] for v in x])
        drawn.bars.append(
            (
                x,
                np.array([p.get_height() for p in patches]),
                np.array([p.get_y() for p in patches]),
                np.array([p.get_width() for p in patches]),
            )
        )
    for line in ax.lines:
        if type(line).__name__ == "AxLine":
            drawn.lines.append((None, None, (line._slope, line._xy1[1])))
        else:
            x, y = line.get_data()
            if categories:
                x = np.array([categories[round(v)] for v in x])
            drawn.lines.append((np.asarray(x), np.asarray(y), None))
    for collection in ax.collections:
        offsets = collection.get_offsets()
        x = offsets[:, 0]
        if categories:
            x = np.array([categories[round(v)] for v in x])
        drawn.points.append((x, offsets[:, 1]))
    return drawn


def extract_xy(chart: Any) -> Drawn:
    r"""Read the primitives drawn in an xy ``Chart``."""
    drawn = Drawn()
    for mark in chart.children:
        if type(mark).__name__ != "Mark":
            continue
        if mark.kind == "bar":
            n = len(mark.x)
            drawn.bars.append(
                (
                    np.asarray(mark.x),
                    np.asarray(mark.y),
                    np.broadcast_to(np.asarray(mark.props["base"], dtype=float), (n,)),
                    np.broadcast_to(np.asarray(mark.props["width"], dtype=float), (n,)),
                )
            )
        elif mark.kind == "line":
            drawn.lines.append((np.asarray(mark.x), np.asarray(mark.y), None))
        elif mark.kind == "scatter":
            drawn.points.append((np.asarray(mark.x), np.asarray(mark.y)))
    return drawn


def extract_bokeh(fig: Any) -> Drawn:
    r"""Read the primitives drawn on a bokeh ``figure``."""
    drawn = Drawn()
    for renderer in fig.renderers:
        glyph = renderer.glyph
        data = renderer.data_source.data
        kind = type(glyph).__name__
        if kind == "VBar":
            x = np.asarray(data["x"])
            n = len(x)
            top, bottom = np.asarray(data["top"]), np.asarray(data["bottom"])
            width = data.get("width", glyph.width)
            drawn.bars.append(
                (x, top - bottom, bottom, np.broadcast_to(np.asarray(width, dtype=float), (n,)))
            )
        elif kind == "Line":
            drawn.lines.append((np.asarray(data["x"]), np.asarray(data["y"]), None))
        elif kind == "Scatter":
            drawn.points.append((np.asarray(data["x"]), np.asarray(data["y"])))
    for annotation in fig.center:
        if type(annotation).__name__ == "Slope":
            drawn.lines.append((None, None, (annotation.gradient, annotation.y_intercept)))
    return drawn


def extract_plotly(traces: Any) -> Drawn:
    r"""Read the primitives drawn by plotly traces."""
    drawn = Drawn()
    for trace in traces:
        if type(trace).__name__ == "Bar":
            x = np.asarray(trace.x)
            n = len(x)
            height = np.asarray(trace.y, dtype=float)
            drawn.bars.append(
                (
                    x,
                    height,
                    np.broadcast_to(np.asarray(trace.base, dtype=float), (n,)),
                    np.broadcast_to(np.asarray(trace.width, dtype=float), (n,)),
                )
            )
        elif trace.mode == "lines":
            drawn.lines.append((np.asarray(trace.x), np.asarray(trace.y), None))
        else:
            drawn.points.append((np.asarray(trace.x), np.asarray(trace.y)))
    return drawn


def _read_csv(text: str) -> dict[str, list[str]]:
    r"""Read the columns of a CSV text."""
    rows = list(csv.DictReader(io.StringIO(text)))
    return {name: [row[name] for row in rows] for name in (rows[0] if rows else {})}


def extract_altair(spec: dict[str, Any], datasets: dict[str, str]) -> Drawn:
    r"""Read the primitives drawn by the layers of an altair chart (a
    ``to_dict()`` of one view, with the ``datasets`` of the chart)."""
    drawn = Drawn()
    for layer in spec.get("layer", [spec]):
        columns = _read_csv(datasets[layer["data"]["name"]])
        mark = layer["mark"]["type"]
        if mark == "bar":
            top = np.array(columns["y"], dtype=float)
            base = np.array(columns["y2"], dtype=float)
            if "x2" in columns:
                lo = np.array(columns["x"], dtype=float)
                hi = np.array(columns["x2"], dtype=float)
                drawn.bars.append(((lo + hi) / 2, top - base, base, hi - lo))
            else:
                width = layer["mark"]["width"]["band"]
                drawn.bars.append(
                    (np.array(columns["x"]), top - base, base, np.full(len(top), width))
                )
        else:
            x = columns["x"]
            x_values = (
                np.array(x)
                if layer["encoding"]["x"]["type"] == "nominal"
                else np.array(x, dtype=float)
            )
            y_values = np.array([float(v) if v else np.nan for v in columns["y"]])
            if mark == "line":
                drawn.lines.append((x_values, y_values, None))
            else:
                drawn.points.append((x_values, y_values))
    return drawn
