r"""Contain the ``Backend`` base class implemented by rendering backends,
plus the small dispatch helpers every backend shares.

Each backend (and each backend's layer renderer) dispatches on
``type(spec)`` against a ``{type: renderer}`` dict. ``resolve_renderer``
and ``check_export_format`` factor out that repeated lookup-or-raise
logic so a backend only owns its dict of renderers, not the dispatch
mechanics around it.
"""

from __future__ import annotations

__all__ = ["Backend", "check_export_format", "resolve_renderer"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Collection
    from pathlib import Path

    from plotmux.specs import BaseSpec

T = TypeVar("T")


def resolve_renderer(
    registry: dict[type[BaseSpec], Callable[..., T]], spec: BaseSpec, backend_name: str
) -> Callable[..., T]:
    r"""Look up the renderer registered for ``type(spec)``.

    Args:
        registry: A ``{spec_type: renderer}`` dict, as owned by a
            backend's ``_RENDERERS`` or a layer module's
            ``_AX_RENDERERS``/``_MARK_RENDERERS``.
        spec: The spec whose type is looked up.
        backend_name: The backend name, used only in the error
            message (e.g. ``"matplotlib"``, ``"xy"``).

    Returns:
        The renderer registered for ``type(spec)``.

    Raises:
        NotImplementedError: if no renderer is registered for
            ``type(spec)``.
    """
    renderer = registry.get(type(spec))
    if renderer is None:
        msg = f"No {backend_name} renderer registered for spec type {type(spec)}"
        raise NotImplementedError(msg)
    return renderer


def check_export_format(fmt: str, supported: Collection[str], backend_name: str) -> None:
    r"""Validate that ``fmt`` is one of ``supported``.

    Args:
        fmt: The requested export format (e.g. ``"png"``).
        supported: The formats the backend supports.
        backend_name: The backend name, used only in the error
            message (e.g. ``"matplotlib"``, ``"xy"``).

    Raises:
        ValueError: if ``fmt`` is not in ``supported``.
    """
    if fmt not in supported:
        msg = (
            f"Unsupported export format {fmt!r} for the {backend_name} backend. "
            f"Supported formats: {sorted(supported)}"
        )
        raise ValueError(msg)


class Backend(ABC):
    r"""Define the interface implemented by a rendering backend.

    A backend turns a backend-agnostic ``BaseSpec`` into its native
    figure object (e.g. a matplotlib ``Figure``) and knows how to export
    that native object to a file.
    """

    name: ClassVar[str]

    @abstractmethod
    def render(self, spec: BaseSpec, **kwargs: Any) -> Any:
        r"""Render a spec into the backend's native figure object.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The backend's native figure object.
        """

    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None:
        r"""Export a native figure object to a file.

        Args:
            native: The native figure object, as returned by
                ``render``.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).
        """
