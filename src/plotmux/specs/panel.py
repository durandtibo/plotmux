r"""Contain the backend-agnostic specification of one axes."""

from __future__ import annotations

__all__ = ["LEGEND_LOCATIONS", "LegendLocation", "PanelSpec"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias, get_args

from plotmux.colors import Color, parse_color
from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import MarkSpec, Spec

if TYPE_CHECKING:
    from collections.abc import Sequence

LegendLocation: TypeAlias = Literal[
    "top_left",
    "top_right",
    "bottom_left",
    "bottom_right",
    "top",
    "bottom",
    "left",
    "right",
]

#: The portable legend locations (there is no ``"best"``: three
#: backends have no automatic placement).
LEGEND_LOCATIONS: frozenset[str] = frozenset(get_args(LegendLocation))

_SCALES = ("linear", "log")
_ORIENTATIONS = ("vertical", "horizontal")


@dataclass(frozen=True, eq=False)
class PanelSpec(Spec):
    r"""Define one axes: the marks drawn on it and its style.

    Several marks on one panel are drawn on shared axes (a layer).
    The marks and the axes style are the only fields: the axes style
    exists once, here, and not on each mark.

    Args:
        marks: The marks to draw, in drawing order. Must be non-empty.
            A panel holds marks only, so a panel cannot nest.
        title: An optional axes title.
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.
        xmin: An optional lower limit of the x-axis. A number, not a
            quantile string. ``None`` leaves the axis autoscaled.
        xmax: An optional upper limit of the x-axis.
        ymin: An optional lower limit of the y-axis.
        ymax: An optional upper limit of the y-axis.
        background_color: An optional background color of the axes.
            Same format as ``MarkSpec.color``. ``None`` uses the
            backend's default.
        legend_title: An optional heading of the legend box. The legend
            exists if and only if one mark has a label.
        legend_location: An optional legend position, one of
            ``LEGEND_LOCATIONS``. ``None`` leaves the backend's
            default.
        legend_orientation: An optional legend layout, ``"vertical"``
            or ``"horizontal"``. ``None`` leaves the backend's
            default.

    Raises:
        InvalidSpecError: if ``marks`` is empty or holds an object
            that is not a ``MarkSpec``, a scale, a legend location or
            a legend orientation is not supported, ``xmin > xmax`` or
            ``ymin > ymax``, the marks mix a categorical x with a numeric x, or
            a mark needs the x extent (a slope) and the panel has none.
            Also a ``ValueError``.
        InvalidColorError: if ``background_color`` is not a valid
            color. Also a ``ValueError``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import HistogramSpec, LineSpec, PanelSpec
        >>> spec = PanelSpec(
        ...     marks=(
        ...         HistogramSpec(values=np.arange(101), bins=10),
        ...         LineSpec(x=np.arange(10), y=np.arange(10)),
        ...     ),
        ...     title="two marks",
        ... )
        >>> len(spec.marks)
        2

        ```
    """

    marks: tuple[MarkSpec, ...]
    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    xscale: Literal["linear", "log"] = "linear"
    yscale: Literal["linear", "log"] = "linear"
    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None
    background_color: Color = None
    legend_title: str | None = None
    legend_location: LegendLocation | None = None
    legend_orientation: Literal["vertical", "horizontal"] | None = None

    def __post_init__(self) -> None:
        marks = tuple(self.marks)
        if not marks:
            msg = "marks must contain at least one mark"
            raise InvalidSpecError(msg)
        for mark in marks:
            if not isinstance(mark, MarkSpec):
                msg = f"marks must hold MarkSpec objects, but received {type(mark).__name__}"
                raise InvalidSpecError(msg)
        object.__setattr__(self, "marks", marks)
        _check_choice("xscale", self.xscale, _SCALES)
        _check_choice("yscale", self.yscale, _SCALES)
        if self.legend_location is not None:
            _check_choice("legend_location", self.legend_location, sorted(LEGEND_LOCATIONS))
        if self.legend_orientation is not None:
            _check_choice("legend_orientation", self.legend_orientation, _ORIENTATIONS)
        _check_order("xmin", self.xmin, "xmax", self.xmax)
        _check_order("ymin", self.ymin, "ymax", self.ymax)
        if self.background_color is not None:
            object.__setattr__(self, "background_color", parse_color(self.background_color))
        kinds = {mark.is_categorical() for mark in marks} - {None}
        if len(kinds) > 1:
            msg = (
                "marks must not mix a categorical x (strings) with a numeric x on the "
                "same axes, but received both"
            )
            raise InvalidSpecError(msg)
        if any(mark.requires_extent for mark in marks) and self.x_extent() is None:
            msg = (
                "a mark needs the x extent of the panel (a slope has no data of its own): "
                "set xmin and xmax, or add a mark with numeric x data to the panel"
            )
            raise InvalidSpecError(msg)

    def x_extent(self) -> tuple[float, float] | None:
        r"""Resolve the x extent of the panel.

        Each bound is the explicit ``xmin``/``xmax`` where it is set,
        else the min/max of the ``x_extent()`` of the marks that have
        data on the x-axis.

        Returns:
            The ``(lo, hi)`` extent, or ``None`` if a bound can be
                resolved neither from the limits nor from the marks.

        Example:
            ```pycon
            >>> import numpy as np
            >>> from plotmux.specs import LineSpec, PanelSpec
            >>> PanelSpec(marks=(LineSpec(x=np.arange(5), y=np.arange(5)),)).x_extent()
            (0.0, 4.0)
            >>> PanelSpec(marks=(LineSpec(x=np.arange(5), y=np.arange(5)),), xmax=10).x_extent()
            (0.0, 10)

            ```
        """
        extents = [e for mark in self.marks if (e := mark.x_extent()) is not None]
        lo = self.xmin if self.xmin is not None else min((e[0] for e in extents), default=None)
        hi = self.xmax if self.xmax is not None else max((e[1] for e in extents), default=None)
        if lo is None or hi is None:
            return None
        return lo, hi


def _check_choice(name: str, value: object, choices: Sequence[str]) -> None:
    r"""Check that a value is one of the choices.

    Args:
        name: The name of the field, used in the message.
        value: The value to check.
        choices: The supported values.

    Raises:
        InvalidSpecError: if ``value`` is not in ``choices``. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> from plotmux.specs.panel import _check_choice
        >>> _check_choice("xscale", "log", ("linear", "log"))

        ```
    """
    if value not in choices:
        msg = f"{name} must be one of {list(choices)}, but received {value!r}"
        raise InvalidSpecError(msg)


def _check_order(low_name: str, low: float | None, high_name: str, high: float | None) -> None:
    r"""Check that a lower bound is not greater than an upper bound.

    Args:
        low_name: The name of the lower bound, used in the message.
        low: The lower bound, or ``None``.
        high_name: The name of the upper bound, used in the message.
        high: The upper bound, or ``None``.

    Raises:
        InvalidSpecError: if both are set and ``low > high``. Also a
            ``ValueError``.

    Example:
        ```pycon
        >>> from plotmux.specs.panel import _check_order
        >>> _check_order("xmin", 0, "xmax", 1)

        ```
    """
    if low is not None and high is not None and low > high:
        msg = (
            f"{low_name} must not be greater than {high_name}, but received "
            f"{low_name}={low} and {high_name}={high}"
        )
        raise InvalidSpecError(msg)
