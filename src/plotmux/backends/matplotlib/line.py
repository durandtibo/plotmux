r"""Render a ``LineSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_line"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import LineSpec


def render_line(ax: Axes, spec: LineSpec, **kwargs: Any) -> Axes:
    r"""Render a ``LineSpec`` onto a matplotlib ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The line spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.plot``.

    Returns:
        The ``Axes`` the line was drawn onto.
    """
    ax.plot(spec.x, spec.y, label=spec.label, color=spec.color, **kwargs)
    if spec.label is not None:
        ax.legend()
    return ax
