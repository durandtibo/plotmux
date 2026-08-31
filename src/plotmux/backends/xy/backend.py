r"""Contain the xy ``Backend`` implementation.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["XyBackend"]

from typing import TYPE_CHECKING, ClassVar

from plotmux.backends.base import Backend, check_export_format, make_renderer
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


class XyBackend(Backend):
    r"""Implement the xy rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "xy"
    supported_formats: ClassVar[frozenset[str]] = frozenset(
        {"png", "jpg", "jpeg", "webp", "svg", "pdf", "html"}
    )

    # ``make_renderer`` (``plotmux.backends.base``) wraps a chart-specific
    # ``(spec, **kwargs) -> Chart`` renderer with ``apply_common_style``. xy
    # has no separate figure/axes object to construct first (unlike
    # matplotlib's/bokeh's own local ``_make_renderer``), so it shares this
    # helper with the ``altair`` backend rather than defining its own.
    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., xy.Chart]]] = {
        HistogramSpec: make_renderer(render_histogram, apply_common_style),
        LineSpec: make_renderer(render_line, apply_common_style),
        ScatterSpec: make_renderer(render_scatter, apply_common_style),
        LayerSpec: make_renderer(render_layer, apply_common_style),
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

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
        check_export_format(fmt, self.supported_formats, self.name)
        native.write_image(path, format=fmt)
