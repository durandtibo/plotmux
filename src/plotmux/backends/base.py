r"""Contain the ``Backend`` base class implemented by rendering backends,
plus the small dispatch helpers every backend shares.

Each backend (and each backend's layer renderer) dispatches on
``type(spec)`` against a ``{type: renderer}`` dict. ``resolve_renderer``
and ``check_export_format`` factor out that repeated lookup-or-raise
logic so a backend only owns its dict of renderers, not the dispatch
mechanics around it.
"""

from __future__ import annotations

__all__ = [
    "Backend",
    "BackendCapabilities",
    "check_export_format",
    "make_renderer",
    "resolve_renderer",
]

import dataclasses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from plotmux.exceptions import UnsupportedFormatError, UnsupportedSpecError

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
        UnsupportedSpecError: if no renderer is registered for
            ``type(spec)``. Also a ``NotImplementedError``, so
            existing ``except NotImplementedError`` code keeps
            working unchanged.
    """
    renderer = registry.get(type(spec))
    if renderer is None:
        msg = f"No {backend_name} renderer registered for spec type {type(spec)}"
        raise UnsupportedSpecError(msg)
    return renderer


def check_export_format(fmt: str, supported: Collection[str], backend_name: str) -> None:
    r"""Validate that ``fmt`` is one of ``supported``.

    Args:
        fmt: The requested export format (e.g. ``"png"``).
        supported: The formats the backend supports.
        backend_name: The backend name, used only in the error
            message (e.g. ``"matplotlib"``, ``"xy"``).

    Raises:
        UnsupportedFormatError: if ``fmt`` is not in ``supported``.
            Also a ``ValueError``, so existing ``except ValueError``
            code keeps working unchanged.
    """
    if fmt not in supported:
        msg = (
            f"Unsupported export format {fmt!r} for the {backend_name} backend. "
            f"Supported formats: {sorted(supported)}"
        )
        raise UnsupportedFormatError(msg)


def make_renderer(
    chart_render: Callable[..., T], style: Callable[[T, BaseSpec], T]
) -> Callable[..., T]:
    r"""Build a ``render(spec, **kwargs) -> native`` function that draws
    then styles in a single step.

    This suits backends with no separate figure/axes object to
    construct up front -- the chart-specific renderer already returns
    the finished native object, and styling (title, labels, scale) is
    applied to that same object afterwards. Both ``altair`` and ``xy``
    follow this shape, so they share this helper instead of each
    defining their own near-identical wrapper.

    Backends that *do* need a construction step first (e.g.
    matplotlib building a ``Figure``/``Axes`` pair, or bokeh passing
    axis type at ``figure()`` construction time) define their own
    local ``_make_renderer`` instead, since that construction step is
    backend-specific and would otherwise leak into this shared helper.

    Args:
        chart_render: The chart-specific ``(spec, **kwargs) -> native``
            renderer to wrap, e.g. ``render_histogram``.
        style: The backend's ``apply_common_style``-shaped function,
            called as ``style(native, spec)`` and returning the
            (possibly new, for immutable native objects) styled
            native object.

    Returns:
        A ``(spec, **kwargs) -> native`` renderer suitable for a
            backend's ``_RENDERERS`` dict.
    """

    def render(spec: BaseSpec, **kwargs: Any) -> T:
        return style(chart_render(spec, **kwargs), spec)

    return render


@dataclasses.dataclass(frozen=True)
class BackendCapabilities:
    r"""Report what a backend supports, for querying ahead of a render or
    export call instead of discovering it via an exception.

    ``spec_types`` answers "does this backend support ``X`` as a
    top-level spec" (e.g. standalone, not just nested in a
    ``LayerSpec``) with no new bookkeeping -- it is exactly
    ``Backend._RENDERERS.keys()``. ``caveats`` covers the partial
    support that a spec-type membership test alone can't express (a
    spec type only supported inside a layer, a field silently
    ignored, an export restriction) -- see ``Backend._CAVEATS``.

    This is descriptive only: nothing here changes render-time or
    export-time behavior, and a caveat not listed here does not mean
    "definitely fully supported," only "no known caveat is on
    record."

    Args:
        backend_name: The backend's ``name`` (e.g. ``"matplotlib"``).
        spec_types: The spec types with a registered top-level
            renderer in this backend.
        caveats: Short, human-readable notes about known partial
            support not implied by ``spec_types`` alone.
    """

    backend_name: str
    spec_types: frozenset[type[BaseSpec]]
    caveats: tuple[str, ...] = ()


class Backend(ABC):
    r"""Define the interface implemented by a rendering backend.

    A backend turns a backend-agnostic ``BaseSpec`` into its native
    figure object (e.g. a matplotlib ``Figure``) and knows how to export
    that native object to a file.
    """

    name: ClassVar[str]

    #: The export formats this backend's ``save`` accepts (e.g.
    #: ``frozenset({"png", "svg"})``). Exposed so callers can introspect
    #: a backend's capabilities (``get_backend("bokeh").supported_formats``)
    #: instead of discovering them only via a ``ValueError`` from ``save``.
    supported_formats: ClassVar[frozenset[str]]

    #: A ``{spec_type: renderer}`` dict, one entry per spec type this
    #: backend supports. ``render`` below dispatches on ``type(spec)``
    #: against this dict via ``resolve_renderer``, so a concrete backend
    #: only ever needs to own this mapping, not the dispatch mechanics
    #: around it -- every backend used to hand-write an identical
    #: ``render`` body doing exactly that lookup-then-call.
    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., Any]]]

    #: Short, explicit notes about partial support this backend has
    #: that membership in ``_RENDERERS`` alone can't express -- e.g. a
    #: spec type only supported nested inside a ``LayerSpec``, or a
    #: spec field the backend silently ignores. Empty by default; a
    #: concrete backend overrides this only where such a caveat is
    #: known. See ``capabilities()``.
    _CAVEATS: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def capabilities(cls) -> BackendCapabilities:
        r"""Report this backend's supported spec types and known partial-
        support caveats.

        Purely additive and read-only: it changes no render-time or
        export-time behavior, it only exposes what ``_RENDERERS`` and
        ``_CAVEATS`` already record. Lets a caller ask "does this
        backend support ``SlopeSpec`` standalone?" programmatically
        instead of hitting ``UnsupportedSpecError`` or searching
        DESIGN.md. See also ``supported_formats`` for export-format
        support.

        Returns:
            This backend's ``BackendCapabilities``.
        """
        return BackendCapabilities(
            backend_name=cls.name,
            spec_types=frozenset(cls._RENDERERS),
            caveats=cls._CAVEATS,
        )

    def render(self, spec: BaseSpec, **kwargs: Any) -> Any:
        r"""Render a spec into the backend's native figure object.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional backend-specific keyword arguments,
                forwarded to the underlying plotting call.

        Returns:
            The backend's native figure object.

        Raises:
            NotImplementedError: if there is no renderer registered
                for the type of ``spec`` in this backend's
                ``_RENDERERS``.
        """
        renderer = resolve_renderer(self._RENDERERS, spec, self.name)
        return renderer(spec, **kwargs)

    @abstractmethod
    def save(self, native: Any, path: Path, fmt: str) -> None:
        r"""Export a native figure object to a file.

        Args:
            native: The native figure object, as returned by
                ``render``.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``).
        """
