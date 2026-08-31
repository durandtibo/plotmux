r"""Render a ``ScatterSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import ScatterSpec


def render_scatter(ax: Axes, spec: ScatterSpec, **kwargs: Any) -> Axes:
    r"""Render a ``ScatterSpec`` onto a matplotlib ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.scatter``. Overrides the spec-derived ``label``/
            ``color``/``s`` when it repeats one of those keys (e.g. a
            shared ``color=`` passed to ``plotmux.layer``/
            ``plotmux.grid``), instead of raising a ``TypeError`` for
            "multiple values for keyword argument".

    Returns:
        The ``Axes`` the markers were drawn onto.
    """
    style = {"label": spec.label, "color": spec.color, "s": spec.size, **kwargs}
    ax.scatter(spec.x, spec.y, **style)
    if spec.label is not None:
        ax.legend()
    return ax
