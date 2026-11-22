r"""Contain the base classes of the backend-agnostic marks."""

from __future__ import annotations

__all__ = ["MarkSpec", "Spec"]

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from plotmux.colors import Color, parse_color
from plotmux.exceptions import InvalidSpecError
from plotmux.utils.equality import ValueObject

if TYPE_CHECKING:
    from plotmux.primitives import Primitive


@dataclass(frozen=True, eq=False)
class Spec(ValueObject):
    r"""Define the base class of the immutable value objects of the
    specs.

    A spec cannot change after its construction: the fields are
    frozen and the arrays are copied and read-only (see
    ``plotmux.utils.to_readonly_array``). Two specs are equal if they
    have the same type and equal fields, where arrays are compared by
    value (a plain dataclass ``==`` raises on an array field). A spec
    holds arrays, so it is not hashable.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import LineSpec
        >>> LineSpec(x=np.arange(3), y=np.arange(3)) == LineSpec(x=np.arange(3), y=np.arange(3))
        True
        >>> LineSpec(x=np.arange(3), y=np.arange(3)) == LineSpec(x=np.arange(3), y=np.arange(1, 4))
        False

        ```
    """


@dataclass(frozen=True, eq=False)
class MarkSpec(Spec):
    r"""Define the base class of the marks: what is drawn on an axes.

    A mark is plain, backend-agnostic data (the data and the style of
    one chart type). It never holds a plotting-library object. The
    axes (title, labels, scales, limits, legend) belong to a
    ``PanelSpec``, not to the mark. A mark turns itself into drawing
    primitives (see ``to_primitives``), so a new chart type is one
    subclass of ``MarkSpec`` and needs no change in a backend when it
    is a composition of ``Bars``, ``Line`` and ``Points``.

    A subclass that has its own ``__post_init__`` must call
    ``super().__post_init__()``.

    Args:
        label: An optional label used in the legend.
        color: An optional color. It can be a hex string
            (``"#rrggbb"`` or ``"#rrggbbaa"``), a CSS/matplotlib named
            color (e.g. ``"tab:blue"``), or an RGB(A) tuple of floats
            in ``[0, 1]``. ``None`` takes the next color of
            ``plotmux.colors.palette.DEFAULT_PALETTE`` (see
            ``plotmux.scene.build_scene``), the same on every backend.
        alpha: An optional opacity, in ``[0, 1]``. ``None`` uses the
            backend's default (fully opaque).

    Raises:
        InvalidSpecError: if ``alpha`` is not in ``[0, 1]``. Also a
            ``ValueError``.
        InvalidColorError: if ``color`` is not a valid color. Also a
            ``ValueError``.
    """

    #: ``True`` if the mark cannot be lowered without the x extent of
    #: its panel (a slope has no data of its own).
    requires_extent: ClassVar[bool] = False

    # ``kw_only=True`` so these defaulted fields can precede the required
    # fields of a subclass (e.g. ``HistogramSpec.values``).
    label: str | None = field(default=None, kw_only=True)
    color: Color = field(default=None, kw_only=True)
    alpha: float | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if self.alpha is not None and not 0.0 <= self.alpha <= 1.0:
            msg = f"alpha must be in the range [0, 1], but received {self.alpha}"
            raise InvalidSpecError(msg)
        if self.color is not None:
            object.__setattr__(self, "color", parse_color(self.color))

    def x_extent(self) -> tuple[float, float] | None:
        r"""Return the x extent of the data of the mark.

        Returns:
            The ``(min, max)`` of the x data, or ``None`` if the mark
                has no numeric x data of its own (a slope, a
                categorical x, no value).
        """
        return None

    def is_categorical(self) -> bool | None:
        r"""Tell whether the mark draws on a categorical x-axis.

        Returns:
            ``True`` for a categorical (string) x, ``False`` for a
                numeric x, and ``None`` if the mark has no x data of
                its own (a slope).
        """
        return None

    def to_primitives(self, extent: tuple[float, float] | None) -> tuple[Primitive, ...]:
        r"""Lower the mark to drawing primitives.

        Args:
            extent: The resolved x extent of the panel (see
                ``PanelSpec.x_extent``), or ``None`` if the panel has
                none. Only a mark with ``requires_extent`` uses it.

        Returns:
            The primitives to draw, in drawing order. A primitive
                whose color is ``None`` gets a palette color from
                ``plotmux.scene.build_scene``.

        Raises:
            NotImplementedError: always, a subclass must override it.
        """
        msg = f"{type(self).__name__} must implement to_primitives"
        raise NotImplementedError(msg)
