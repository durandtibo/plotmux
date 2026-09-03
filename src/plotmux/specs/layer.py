r"""Contain the backend-agnostic layering specification."""

from __future__ import annotations

__all__ = ["LayerSpec"]

from dataclasses import dataclass, replace

from plotmux.colors.palette import DEFAULT_PALETTE
from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec, XBoundSpec


@dataclass(frozen=True)
class LayerSpec(XBoundSpec):
    r"""Define a spec that draws multiple child specs on one shared
    axes.

    Args:
        layers: The child specs to draw together, in draw order.
            Must be non-empty. A ``LayerSpec`` nested inside
            ``layers`` is rejected: layering is designed as one flat
            pass over ``layers`` (see
            ``plotmux.backends.matplotlib.layer.render_layer`` and
            ``plotmux.backends.xy.layer.render_layer``), so callers
            must flatten nested layers themselves rather than relying
            on recursive dispatch.

    Raises:
        ValueError: if ``layers`` is empty or contains a
            ``LayerSpec``.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.specs import HistogramSpec, LayerSpec, LineSpec
        >>> spec = LayerSpec(
        ...     layers=(
        ...         HistogramSpec(values=np.arange(101), bins=10),
        ...         LineSpec(x=np.arange(10), y=np.arange(10)),
        ...     )
        ... )
        >>> len(spec.layers)
        2

        ```
    """

    layers: tuple[BaseSpec, ...]

    def __post_init__(self) -> None:
        if not self.layers:
            msg = "layers must contain at least one spec"
            raise InvalidSpecError(msg)
        if any(isinstance(child, LayerSpec) for child in self.layers):
            msg = "layers must not contain a LayerSpec (nesting is not supported)"
            raise InvalidSpecError(msg)
        object.__setattr__(self, "layers", tuple(_assign_default_colors(self.layers)))
        self._validate_base()


def _assign_default_colors(layers: tuple[BaseSpec, ...]) -> tuple[BaseSpec, ...]:
    r"""Give each color-carrying child with no explicit ``color`` a
    distinct color from ``DEFAULT_PALETTE``, cycling through it in draw
    order.

    Every backend renders an uncolored child by passing its
    ``color=None`` straight to the underlying plotting call.
    matplotlib auto-cycles colors for repeated ``color=None`` calls on
    the same ``Axes``, but bokeh/altair/xy do not, so the same
    ``LayerSpec`` used to render with distinct series colors under
    matplotlib and identical/overlapping colors everywhere else.
    Assigning the colors here, once, backend-agnostically, makes every
    backend agree.

    A child with an explicit ``color`` is left untouched and does not
    consume a palette slot, so mixing explicit and default colors
    still cycles the palette only across the children that need it.

    Args:
        layers: The child specs to assign default colors to.

    Returns:
        The same children, in the same order, with ``color=None``
            replaced by a palette color on each one that has a
            ``color`` field.
    """
    result = []
    i = 0
    for child in layers:
        # ``color`` is not a field on ``BaseSpec`` itself (``GridSpec`` has
        # none), so it is looked up dynamically rather than narrowed by
        # ``isinstance`` against every current and future color-carrying
        # spec type.
        if getattr(child, "color", "unset") is None:
            result.append(replace(child, color=DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]))
            i += 1
        else:
            result.append(child)
    return tuple(result)
