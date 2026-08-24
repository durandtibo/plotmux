r"""Contain the xy ``Backend`` implementation.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["XyBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

from plotmux.backends.base import Backend
from plotmux.backends.xy.histogram import render_histogram
from plotmux.core.specs import BaseSpec, HistogramSpec

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import xy

_SUPPORTED_FORMATS = frozenset({"png", "jpg", "jpeg", "webp", "svg", "pdf", "html"})


class XyBackend(Backend):
    r"""Implement the xy rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "xy"

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., xy.Chart]]] = {
        HistogramSpec: render_histogram,
    }

    def render(self, spec: BaseSpec, **kwargs: Any) -> xy.Chart:
        r"""Render a spec into an xy ``Chart``.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional xy-specific keyword arguments,
                forwarded to the underlying mark constructor.

        Returns:
            The resulting xy ``Chart``.

        Raises:
            NotImplementedError: if there is no xy renderer
                registered for the type of ``spec``.
        """
        renderer = self._RENDERERS.get(type(spec))
        if renderer is None:
            msg = f"No xy renderer registered for spec type {type(spec)}"
            raise NotImplementedError(msg)
        return renderer(spec, **kwargs)

    def save(self, native: xy.Chart, path: Path, fmt: str) -> None:
        r"""Export an xy ``Chart`` to a file.

        Args:
            native: The xy ``Chart`` to export.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``,
                ``"html"``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        if fmt not in _SUPPORTED_FORMATS:
            msg = (
                f"Unsupported export format {fmt!r} for the xy backend. "
                f"Supported formats: {sorted(_SUPPORTED_FORMATS)}"
            )
            raise ValueError(msg)
        native.write_image(path, format=fmt)
