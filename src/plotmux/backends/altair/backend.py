r"""Contain the altair ``Backend`` implementation.

This module is only imported when altair is installed (see
``plotmux.backends.altair.__init__``), so it can import altair
unconditionally.
"""

from __future__ import annotations

__all__ = ["AltairBackend"]

from typing import TYPE_CHECKING, Any, ClassVar, cast

from plotmux.backends.altair.histogram import render_histogram
from plotmux.backends.altair.layer import render_layer
from plotmux.backends.altair.line import render_line
from plotmux.backends.altair.scatter import render_scatter
from plotmux.backends.altair.style import apply_common_style
from plotmux.backends.base import Backend, check_export_format, resolve_renderer
from plotmux.specs import BaseSpec, HistogramSpec, LayerSpec, LineSpec, ScatterSpec

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from typing import Literal

    import altair as alt

# Only ``html``/``json`` are supported natively: static image export
# (``png``/``svg``/``pdf``) goes through altair's ``vl-convert-python``
# integration, an additional package (bundling its own Rust-based Vega-Lite
# renderer) beyond "pip install altair" -- the same rationale as bokeh's
# `png`/`svg` requiring a Selenium webdriver (see
# ``plotmux.backends.bokeh.backend``). ``html`` is altair's standalone,
# openable-in-a-browser export; ``json`` is the raw Vega-Lite spec, useful
# for embedding in another Vega-Lite-aware tool.
_SUPPORTED_FORMATS = frozenset({"html", "json"})


def _make_renderer(
    chart_render: Callable[..., alt.typing.ChartType],
) -> Callable[..., alt.typing.ChartType]:
    r"""Build a ``render(spec, **kwargs) -> Chart`` function from a
    ``chart_render(spec, **kwargs) -> Chart`` function.

    Every entry in ``_RENDERERS`` shares the same two steps: build the
    spec-specific mark via ``chart_render``, then apply the fields
    common to every chart type (title, labels, scale) via
    ``apply_common_style``. Factoring that out here means adding a new
    chart type to this backend is exactly one ``_RENDERERS`` entry --
    ``_make_renderer(render_x)`` -- rather than a new hand-written
    wrapper function that repeats the same two lines. Mirrors
    ``plotmux.backends.xy.backend``, where ``XyBackend.render`` does
    the equivalent two-step call generically since every xy
    ``render_<type>`` already takes only ``(spec, **kwargs)`` (no
    figure/axes object to create first, unlike matplotlib's/bokeh's
    ``_make_renderer``).

    Args:
        chart_render: The chart-specific ``(spec, **kwargs) -> Chart``
            renderer to wrap, e.g. ``render_histogram``.

    Returns:
        A ``(spec, **kwargs) -> Chart`` renderer suitable for
            ``_RENDERERS``.
    """

    def render(spec: BaseSpec, **kwargs: Any) -> alt.typing.ChartType:
        return apply_common_style(chart_render(spec, **kwargs), spec)

    return render


class AltairBackend(Backend):
    r"""Implement the altair rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "altair"

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., alt.typing.ChartType]]] = {
        HistogramSpec: _make_renderer(render_histogram),
        LineSpec: _make_renderer(render_line),
        ScatterSpec: _make_renderer(render_scatter),
        LayerSpec: _make_renderer(render_layer),
    }

    def render(self, spec: BaseSpec, **kwargs: Any) -> alt.typing.ChartType:
        r"""Render a spec into an altair ``Chart``.

        Args:
            spec: The backend-agnostic spec to render.
            **kwargs: Additional altair-specific keyword arguments,
                forwarded to the underlying mark constructor.

        Returns:
            The resulting altair ``Chart``.

        Raises:
            NotImplementedError: if there is no altair renderer
                registered for the type of ``spec``.
        """
        renderer = resolve_renderer(self._RENDERERS, spec, self.name)
        return renderer(spec, **kwargs)

    def save(self, native: alt.typing.ChartType, path: Path, fmt: str) -> None:
        r"""Export an altair ``Chart`` to a file.

        Args:
            native: The altair ``Chart`` to export.
            path: The path where to save the figure.
            fmt: The export format. Only ``"html"``/``"json"`` are
                supported (see ``_SUPPORTED_FORMATS``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        check_export_format(fmt, _SUPPORTED_FORMATS, self.name)
        # ``fmt`` is checked against ``_SUPPORTED_FORMATS`` (``{"html", "json"}``)
        # above, so it is safe to narrow it to ``Chart.save``'s ``Literal``
        # format type -- pyright cannot infer that narrowing from the runtime
        # ``check_export_format`` call alone.
        native.save(str(path), format=cast("Literal['html', 'json']", fmt))
