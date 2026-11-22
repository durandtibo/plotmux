r"""Contain the backend-agnostic slope (abline) specification."""

from __future__ import annotations

__all__ = ["SlopeSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Literal

import numpy as np

from plotmux.colors import parse_optional_color
from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Line
from plotmux.specs.base import MarkSpec

if TYPE_CHECKING:
    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class SlopeSpec(MarkSpec):
    r"""Define a backend-agnostic slope (a.k.a. abline) mark.

    Unlike ``LineSpec``, which is data-bound (an explicit ``x``/``y``
    pair), a ``SlopeSpec`` describes a line by its closed form,
    ``y = gradient * x + intercept``, with no data of its own. It is
    drawn as the segment over the x extent of its panel: the
    ``xmin``/``xmax`` of the ``PanelSpec`` where they are set, else the
    extent of the data of the other marks of the panel. A panel with a
    slope and no x extent raises an ``InvalidSpecError``.

    Args:
        gradient: The line's slope.
        intercept: The line's y-intercept (the ``y`` value at
            ``x = 0``).
        linewidth: An optional line width. ``None`` uses the
            backend's default width.
        linestyle: The line's dash style.

    ``label``, ``color`` and ``alpha`` are inherited from
    ``MarkSpec``.

    Raises:
        InvalidSpecError: if ``alpha`` is not in ``[0, 1]``. Also a
            ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> from plotmux.specs import SlopeSpec
        >>> spec = SlopeSpec(gradient=2, intercept=10)
        >>> spec.gradient
        2

        ```
    """

    requires_extent: ClassVar[bool] = True

    gradient: float
    intercept: float = 0.0
    linewidth: float | None = None
    linestyle: Literal["solid", "dashed", "dotted", "dashdot"] = "solid"

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        r"""Lower the slope to the segment over the x extent.

        Args:
            extent: The x extent of the panel.

        Returns:
            One ``Line`` with the two endpoints of the extent. Its
                ``infinite`` field is ``(gradient, intercept)``.

        Raises:
            InvalidSpecError: if ``extent`` is ``None``. Also a
                ``ValueError``.
        """
        if extent is None:
            msg = (
                "a SlopeSpec needs the x extent of its panel: set xmin and xmax, or add "
                "a mark with x data to the panel"
            )
            raise InvalidSpecError(msg)
        x = np.array(extent, dtype=float)
        return (
            Line(
                x=x,
                y=self.gradient * x + self.intercept,
                infinite=(float(self.gradient), float(self.intercept)),
                color=parse_optional_color(self.color),
                alpha=self.alpha,
                linewidth=self.linewidth,
                linestyle=self.linestyle,
                label=self.label,
            ),
        )
