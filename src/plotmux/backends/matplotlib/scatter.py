r"""Render a ``ScatterSpec`` onto a matplotlib ``Axes``."""

from __future__ import annotations

__all__ = ["MARKER_STYLE", "render_scatter"]

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import ScatterSpec

#: Maps ``ScatterSpec.marker``'s portable shape name to matplotlib's own
#: single-character/string ``Axes.scatter(marker=...)`` code. Shared by
#: this module only (matplotlib is the only backend needing a translation
#: table for every one of the six portable names -- bokeh and xy accept
#: them directly, see ``plotmux.backends.bokeh.scatter``/
#: ``plotmux.backends.xy.scatter``).
MARKER_STYLE = {
    "circle": "o",
    "square": "s",
    "triangle": "^",
    "diamond": "D",
    "cross": "+",
    "x": "x",
}


def render_scatter(ax: Axes, spec: ScatterSpec, **kwargs: Any) -> Axes:
    r"""Render a ``ScatterSpec`` onto a matplotlib ``Axes``.

    Args:
        ax: The matplotlib ``Axes`` to draw onto.
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``Axes.scatter``. Overrides the spec-derived ``label``/
            ``color``/``s``/``edgecolors``/``alpha``/``marker`` when
            it repeats one of those keys (e.g. a shared ``color=``
            passed to ``plotmux.layer``/``plotmux.grid``), instead of
            raising a ``TypeError`` for "multiple values for keyword
            argument".

    Returns:
        The ``Axes`` the markers were drawn onto.
    """
    style = {
        "label": spec.label,
        "color": spec.color,
        "s": spec.size,
        "alpha": spec.alpha,
        **kwargs,
    }
    # ``Axes.scatter``'s own ``edgecolors`` (plural) parameter defaults to
    # ``"face"`` (edge matches fill), which is already what happens by not
    # setting it at all -- so it is only added when ``spec.edgecolor`` is
    # explicitly set, letting matplotlib's own default take over otherwise.
    if spec.edgecolor is not None:
        style.setdefault("edgecolors", spec.edgecolor)
    if spec.fill is False:
        # ``facecolors="none"`` draws a hollow marker: no fill, only the
        # outline (``edgecolors``, defaulting to ``spec.color`` when
        # ``spec.edgecolor`` is unset via the ``setdefault`` above --
        # matplotlib's own default ``edgecolors="face"`` would otherwise
        # match the (now-transparent) face, drawing nothing at all).
        # ``Axes.scatter`` rejects passing both ``color`` and
        # ``facecolors``/``edgecolors`` at once ("Supply a 'c' argument or
        # a 'color' kwarg but not both"), so ``color`` is popped in favor
        # of the explicit pair.
        style.pop("color", None)
        style["facecolors"] = "none"
        style.setdefault("edgecolors", spec.color)
    if spec.marker is not None:
        style.setdefault("marker", MARKER_STYLE[spec.marker])
    ax.scatter(spec.x, spec.y, **style)
    if spec.label is not None:
        ax.legend()
    return ax
