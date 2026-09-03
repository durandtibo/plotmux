r"""Contain the altair ``Backend`` implementation.

This module is only imported when altair is installed (see
``plotmux.backends.altair.__init__``), so it can import altair
unconditionally.
"""

from __future__ import annotations

__all__ = ["AltairBackend"]

from typing import TYPE_CHECKING, ClassVar, cast

from plotmux.backends.altair.bar import render_bar
from plotmux.backends.altair.cdf import render_cdf
from plotmux.backends.altair.grid import render_grid
from plotmux.backends.altair.histogram import render_histogram
from plotmux.backends.altair.layer import render_layer
from plotmux.backends.altair.line import render_line
from plotmux.backends.altair.scatter import render_scatter
from plotmux.backends.altair.stacked_bar import render_stacked_bar
from plotmux.backends.altair.style import apply_common_style
from plotmux.backends.base import Backend, check_export_format, make_renderer
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
    from typing import Literal

    import altair as alt


class AltairBackend(Backend):
    r"""Implement the altair rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "altair"
    # Only ``html``/``json`` are supported natively: static image export
    # (``png``/``svg``/``pdf``) goes through altair's ``vl-convert-python``
    # integration, an additional package (bundling its own Rust-based
    # Vega-Lite renderer) beyond "pip install altair" -- the same rationale
    # as bokeh's `png`/`svg` requiring a Selenium webdriver (see
    # ``plotmux.backends.bokeh.backend``). ``html`` is altair's standalone,
    # openable-in-a-browser export; ``json`` is the raw Vega-Lite spec,
    # useful for embedding in another Vega-Lite-aware tool.
    supported_formats: ClassVar[frozenset[str]] = frozenset({"html", "json"})

    # ``make_renderer`` (``plotmux.backends.base``) wraps a chart-specific
    # ``(spec, **kwargs) -> Chart`` renderer with ``apply_common_style``.
    # Altair has no separate figure/axes object to construct first (unlike
    # matplotlib's/bokeh's own local ``_make_renderer``), so it shares this
    # helper with the ``xy`` backend rather than defining its own.
    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., alt.typing.ChartType]]] = {
        HistogramSpec: make_renderer(render_histogram, apply_common_style),
        BarSpec: make_renderer(render_bar, apply_common_style),
        StackedBarSpec: make_renderer(render_stacked_bar, apply_common_style),
        CdfSpec: make_renderer(render_cdf, apply_common_style),
        LineSpec: make_renderer(render_line, apply_common_style),
        ScatterSpec: make_renderer(render_scatter, apply_common_style),
        LayerSpec: make_renderer(render_layer, apply_common_style),
        # ``render_grid`` builds and styles each cell independently, then
        # concatenates them -- it does not fit ``make_renderer``'s "one
        # chart-level render call, one shared style call" shape, so it is
        # registered directly instead of wrapped.
        GridSpec: render_grid,
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

    def save(self, native: alt.typing.ChartType, path: Path, fmt: str) -> None:
        r"""Export an altair ``Chart`` to a file.

        Args:
            native: The altair ``Chart`` to export.
            path: The path where to save the figure.
            fmt: The export format. Only ``"html"``/``"json"`` are
                supported (see ``supported_formats``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        check_export_format(fmt, self.supported_formats, self.name)
        # ``fmt`` is checked against ``supported_formats`` (``{"html", "json"}``)
        # above, so it is safe to narrow it to ``Chart.save``'s ``Literal``
        # format type -- pyright cannot infer that narrowing from the runtime
        # ``check_export_format`` call alone.
        native.save(str(path), format=cast("Literal['html', 'json']", fmt))
