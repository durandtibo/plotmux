r"""Contain the backend-agnostic layering specification."""

from __future__ import annotations

__all__ = ["LayerSpec"]

from dataclasses import dataclass

from plotmux.exceptions import InvalidSpecError
from plotmux.specs.base import BaseSpec


@dataclass(frozen=True)
class LayerSpec(BaseSpec):
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
