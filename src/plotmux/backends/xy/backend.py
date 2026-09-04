r"""Contain the xy ``Backend`` implementation.

This module is only imported when xy is installed (see
``plotmux.backends.xy.__init__``), so it can import xy unconditionally.
"""

from __future__ import annotations

__all__ = ["XyBackend"]

from typing import TYPE_CHECKING, ClassVar

from plotmux.backends.base import Backend, check_export_format, make_renderer
from plotmux.backends.xy.bar import render_bar
from plotmux.backends.xy.cdf import render_cdf
from plotmux.backends.xy.grid import XyGrid, render_grid, render_grid_html
from plotmux.backends.xy.histogram import render_histogram
from plotmux.backends.xy.layer import render_layer
from plotmux.backends.xy.line import render_line
from plotmux.backends.xy.scatter import render_scatter
from plotmux.backends.xy.stacked_bar import render_stacked_bar
from plotmux.backends.xy.style import apply_common_style
from plotmux.exceptions import UnsupportedFormatError
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
    StackedBarSpec,
)

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

    # See ``Backend._CAVEATS``/``capabilities()``. ``SlopeSpec`` has no
    # entry in ``_RENDERERS`` below -- it renders only nested inside a
    # ``LayerSpec`` (see ``plotmux.backends.xy.layer``/``.slope``), not
    # standalone. The ``GridSpec`` export restriction is also
    # ``supported_formats``-discoverable per-format, but not as a
    # "html-only, and only for a grid" statement -- see ``save``'s
    # docstring and ``XyGrid``.
    _CAVEATS: ClassVar[tuple[str, ...]] = (
        "SlopeSpec is only supported nested inside a LayerSpec, not standalone.",
        (
            "GridSpec export supports 'html' only, unlike every other spec "
            "type on this backend: xy has no chart-composition primitive "
            "for arranging independent panels into one PNG/SVG/PDF."
        ),
    )

    # ``make_renderer`` (``plotmux.backends.base``) wraps a chart-specific
    # ``(spec, **kwargs) -> Chart`` renderer with ``apply_common_style``. xy
    # has no separate figure/axes object to construct first (unlike
    # matplotlib's/bokeh's own local ``_make_renderer``), so it shares this
    # helper with the ``altair`` backend rather than defining its own.
    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., xy.Chart]]] = {
        HistogramSpec: make_renderer(render_histogram, apply_common_style),
        BarSpec: make_renderer(render_bar, apply_common_style),
        StackedBarSpec: make_renderer(render_stacked_bar, apply_common_style),
        CdfSpec: make_renderer(render_cdf, apply_common_style),
        LineSpec: make_renderer(render_line, apply_common_style),
        ScatterSpec: make_renderer(render_scatter, apply_common_style),
        LayerSpec: make_renderer(render_layer, apply_common_style),
        # ``GridSpec`` is *not* wrapped in ``make_renderer``: unlike every
        # other entry, ``render_grid`` returns an ``XyGrid``, not a bare
        # ``xy.Chart``, and title/labels/scale have no grid-level meaning
        # (each cell already styled itself, see ``render_grid``) -- same
        # rationale as matplotlib's/bokeh's/altair's own ``GridSpec`` entry.
        GridSpec: render_grid,
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

    def save(self, native: xy.Chart | XyGrid, path: Path, fmt: str) -> None:
        r"""Export an xy ``Chart`` or ``XyGrid`` to a file.

        Args:
            native: The xy ``Chart`` (any spec type but ``GridSpec``)
                or ``XyGrid`` (a rendered ``GridSpec``, see
                ``plotmux.backends.xy.grid``) to export.
            path: The path where to save the figure.
            fmt: The export format (e.g. ``"png"``, ``"svg"``,
                ``"html"``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format,
                or ``native`` is an ``XyGrid`` and ``fmt`` is not
                ``"html"`` (see ``XyGrid``'s docstring for why grid
                export is HTML-only).
        """
        check_export_format(fmt, self.supported_formats, self.name)
        if isinstance(native, XyGrid):
            if fmt != "html":
                msg = (
                    f"Unsupported export format {fmt!r} for an xy grid: only "
                    f"'html' is supported. xy has no chart-composition "
                    f"primitive for arranging independent panels (see "
                    f"XyGrid's docstring), so a grid's per-cell charts can "
                    f"only be composed as separate, embedded documents in "
                    f"one HTML page, not rasterized into one PNG/SVG/PDF."
                )
                raise UnsupportedFormatError(msg)
            path.write_text(render_grid_html(native), encoding="utf-8")
        else:
            native.write_image(path, format=fmt)
