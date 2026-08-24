r"""Apply the common figure-level style fields onto a matplotlib
``Axes``.

This module is only imported when matplotlib is installed (see
``plotmux.backends.matplotlib.__init__``), so it can import matplotlib
unconditionally.
"""

from __future__ import annotations

__all__ = ["apply_common_style"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotmux.specs import BaseSpec


def apply_common_style(ax: Axes, spec: BaseSpec) -> Axes:
    r"""Apply the common figure-level style fields onto an ``Axes``.

    Applies ``title``/``xlabel``/``ylabel``/``xscale``/``yscale`` from
    ``spec`` (defined on ``BaseSpec``, shared by every chart type).
    Called once per backend, right after the chart-specific renderer
    has drawn its mark, so a new chart type gets title/label/scale
    support for free.

    Args:
        ax: The matplotlib ``Axes`` to style.
        spec: The spec whose common style fields to apply.

    Returns:
        The ``Axes`` that was styled.
    """
    if spec.title is not None:
        ax.set_title(spec.title)
    if spec.xlabel is not None:
        ax.set_xlabel(spec.xlabel)
    if spec.ylabel is not None:
        ax.set_ylabel(spec.ylabel)
    ax.set_xscale(spec.xscale)
    ax.set_yscale(spec.yscale)
    return ax
