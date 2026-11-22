r"""Read the primitives back from a native figure.

``extract_<backend>(native)`` returns the primitives a native figure
draws, so the conformance test can check that every backend draws the
same numbers as ``plotmux.scene.build_scene``.
"""

from __future__ import annotations

__all__ = ["Drawn", "expected", "extract_matplotlib", "extract_xy"]

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
