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
            ``Axes.plot``. Overrides the spec-derived ``label``/
            ``color`` when it repeats one of those keys (e.g. a
            shared ``color=`` passed to ``plotmux.layer``/
            ``plotmux.grid``), instead of raising a ``TypeError`` for
            "multiple values for keyword argument".

    Returns:
        The ``Axes`` the line was drawn onto.
    """
    style = {"label": spec.label, "color": spec.color, **kwargs}
    ax.plot(spec.x, spec.y, **style)
    if spec.label is not None:
        ax.legend()
    return ax
