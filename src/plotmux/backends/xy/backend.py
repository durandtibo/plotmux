r"""Contain the xy ``Backend`` implementation.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["XyBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

from plotmux.backends.base import Backend, check_export_format, resolve_renderer
from plotmux.backends.xy.histogram import render_histogram
from plotmux.backends.xy.layer import render_layer
from plotmux.backends.xy.line import render_line
from plotmux.backends.xy.scatter import render_scatter
from plotmux.backends.xy.style import apply_common_style
from plotmux.specs import BaseSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec

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
        LineSpec: render_line,
        ScatterSpec: render_scatter,
        LayerSpec: render_layer,
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
        renderer = resolve_renderer(self._RENDERERS, spec, self.name)
        return apply_common_style(renderer(spec, **kwargs), spec)

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
        check_export_format(fmt, _SUPPORTED_FORMATS, self.name)
        native.write_image(path, format=fmt)
