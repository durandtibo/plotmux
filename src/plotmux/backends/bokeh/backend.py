r"""Contain the bokeh ``Backend`` implementation.

This module is only imported when bokeh is installed (see
``plotmux.backends.bokeh.__init__``), so it can import bokeh
unconditionally.
"""

from __future__ import annotations

__all__ = ["BokehBackend"]

from typing import TYPE_CHECKING, Any, ClassVar

from bokeh.models import Title
from bokeh.plotting import figure as bokeh_figure
from bokeh.plotting import save as bokeh_save
from bokeh.resources import CDN

from plotmux.backends.base import Backend, check_export_format
from plotmux.backends.bokeh.bar import render_bar
from plotmux.backends.bokeh.cdf import render_cdf
from plotmux.backends.bokeh.grid import render_grid
from plotmux.backends.bokeh.histogram import render_histogram
from plotmux.backends.bokeh.layer import render_layer
from plotmux.backends.bokeh.line import render_line
from plotmux.backends.bokeh.scatter import render_scatter
from plotmux.backends.bokeh.style import apply_common_style
from plotmux.specs import (
    BarSpec,
    BaseSpec,
    CdfSpec,
    GridSpec,
    HistogramSpec,
    LayerSpec,
    LineSpec,
    ScatterSpec,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from bokeh.models import LayoutDOM
    from bokeh.plotting import figure as Figure  # noqa: N812


def _make_renderer(
    fig_render: Callable[..., Figure],
) -> Callable[..., Figure]:
    r"""Build a ``render(spec, **kwargs) -> Figure`` function from a
    ``fig_render(fig, spec, **kwargs) -> Figure`` function.

    Every entry in ``_RENDERERS`` shares the same three steps: create
    a ``figure``, draw the spec-specific glyph onto it via
    ``fig_render``, then apply the fields common to every chart type
    (title, labels) via ``apply_common_style``. Factoring that out
    here means adding a new chart type to this backend is exactly one
    ``_RENDERERS`` entry -- ``_make_renderer(render_x)`` -- rather
    than a new hand-written wrapper function that repeats the same
    three lines. Mirrors
    ``plotmux.backends.matplotlib.backend._make_renderer``.

    ``x_axis_type``/``y_axis_type`` are passed to the ``figure``
    constructor here, from ``spec.xscale``/``spec.yscale``, rather
    than being applied by ``apply_common_style`` afterwards: unlike
    matplotlib's ``Axes.set_xscale``, bokeh's axis type is a
    construction-time argument of ``bokeh.plotting.figure``, not a
    property that can be changed once glyphs have been added (see
    ``plotmux.backends.bokeh.style.apply_common_style``).

    Args:
        fig_render: The chart-specific ``(fig, spec, **kwargs) ->
            Figure`` renderer to wrap, e.g. ``render_histogram``.

    Returns:
        A ``(spec, **kwargs) -> Figure`` renderer suitable for
            ``_RENDERERS``.
    """

    def render(spec: BaseSpec, **kwargs: Any) -> Figure:
        fig = bokeh_figure(x_axis_type=spec.xscale, y_axis_type=spec.yscale)
        fig_render(fig, spec, **kwargs)
        apply_common_style(fig, spec)
        return fig

    return render


class BokehBackend(Backend):
    r"""Implement the bokeh rendering backend.

    One renderer function is registered per supported spec type in
    ``_RENDERERS``. Adding a new chart type to this backend means
    adding one entry here; it never grows an if/elif chain.
    """

    name: ClassVar[str] = "bokeh"
    # Only ``html`` is supported: static image export (``png``/``svg``) goes
    # through bokeh's ``export_png``/``export_svg``, which additionally
    # require a Selenium webdriver (a browser binary, not a pip-installable
    # Python package) at runtime -- a heavier, environment-specific
    # dependency than "pip install bokeh". ``html`` is bokeh's own native,
    # dependency-free export path (``bokeh.plotting.save``) and is also the
    # format that best matches why a bokeh backend is worth having (see
    # DESIGN.md 6.1): interactive, standalone HTML output.
    supported_formats: ClassVar[frozenset[str]] = frozenset({"html"})

    _RENDERERS: ClassVar[dict[type[BaseSpec], Callable[..., Figure | LayoutDOM]]] = {
        HistogramSpec: _make_renderer(render_histogram),
        BarSpec: _make_renderer(render_bar),
        CdfSpec: _make_renderer(render_cdf),
        LineSpec: _make_renderer(render_line),
        ScatterSpec: _make_renderer(render_scatter),
        LayerSpec: _make_renderer(render_layer),
        # ``render_grid`` builds and arranges its own independent
        # per-cell ``figure``s into a layout rather than drawing onto one
        # shared ``figure`` -- it does not fit ``_make_renderer``'s
        # "one figure, one fig_render call" shape, so it is registered
        # directly instead of wrapped.
        GridSpec: render_grid,
    }

    # ``render`` is inherited from ``Backend``: it dispatches on
    # ``type(spec)`` against ``_RENDERERS`` above, so this backend does not
    # need its own copy of that dispatch body.

    def save(self, native: Figure | LayoutDOM, path: Path, fmt: str) -> None:
        r"""Export a bokeh ``figure`` to a file.

        Args:
            native: The bokeh ``figure`` to export.
            path: The path where to save the figure.
            fmt: The export format. Only ``"html"`` is supported (see
                ``supported_formats``).

        Raises:
            ValueError: if ``fmt`` is not a supported export format.
        """
        check_export_format(fmt, self.supported_formats, self.name)
        # ``native.title`` only exists on a plain ``figure`` (typed
        # ``Title | str | None`` -- bokeh accepts a bare string as shorthand
        # when *setting* it, but always returns a ``Title`` instance when
        # *read back*, per ``apply_common_style`` only ever assigning a
        # ``str``); a ``GridSpec``'s layout (``gridplot``/``column``, see
        # ``plotmux.backends.bokeh.grid.render_grid``) has no such
        # attribute at all, hence ``getattr(..., None)`` rather than
        # ``native.title`` directly.
        title = getattr(native, "title", None)
        title_text = str(title.text) if isinstance(title, Title) else title
        # ``resources=CDN`` and an explicit ``title`` are passed so bokeh
        # doesn't emit "no resources/title supplied" warnings -- this is the
        # standalone-HTML-with-CDN-assets export path, not bokeh's server mode.
        bokeh_save(
            native,
            filename=str(path),
            resources=CDN,
            title=title_text or "Bokeh Plot",
        )
