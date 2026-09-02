r"""Render a ``BarSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["render_bar"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import BarSpec


def render_bar(ax: Axes, spec: BarSpec, **kwargs: Any) -> Axes:
    r"""Render a ``BarSpec`` onto a matplotlib ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The bar spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.bar``. Overrides the spec-derived ``width``/
            ``label``/``color`` when it repeats one of those keys
            (e.g. a shared ``color=`` passed to ``plotmux.layer``/
            ``plotmux.grid``), instead of raising a ``TypeError`` for
            "multiple values for keyword argument".

    Returns:
        The ``Axes`` the bars were drawn onto.
    """
    style = {"width": spec.width, "label": spec.label, "color": spec.color, **kwargs}
    ax.bar(spec.x, spec.y, **style)
    if spec.label is not None:
        ax.legend()
    return ax
