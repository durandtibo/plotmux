r"""Render a ``ScatterSpec`` into an altair ``Chart``."""

from __future__ import annotations

__all__ = ["render_scatter"]

from typing import TYPE_CHECKING, Any, cast

import altair as alt

from plotmux.backends.altair.style import MARKER_STYLE, prepare_color, rgba_to_altair

if TYPE_CHECKING:
    from plotmux.specs import ScatterSpec


def render_scatter(spec: ScatterSpec, **kwargs: Any) -> alt.Chart:
    r"""Render a ``ScatterSpec`` into an altair ``Chart``.

    The quantitative channels are encoded under the field names
    ``"x"``/``"y"``, the fixed convention every renderer in this
    backend follows so that
    ``plotmux.backends.altair.style.apply_common_style`` can restyle
    them generically after the fact.

    Args:
        spec: The scatter spec to render.
        **kwargs: Additional keyword arguments forwarded to
            ``alt.Chart.mark_point``.

    Returns:
        The resulting altair ``Chart``.
    """
    data = [{"x": x, "y": y} for x, y in zip(spec.x, spec.y)]
    # ``spec.color``/``spec.edgecolor``, once set, are already canonical
    # RGBA tuples: they went through ``parse_color`` in
    # ``ScatterSpec.__post_init__``.
    color = (
        None
        if spec.color is None
        else rgba_to_altair(cast("tuple[float, float, float, float]", spec.color))
    )
    if spec.size is not None:
        kwargs.setdefault("size", spec.size)
    if spec.alpha is not None:
        kwargs.setdefault("opacity", spec.alpha)
    if spec.edgecolor is not None:
        # altair has no field-based encoding channel for a mark's stroke
        # (unlike ``color``, see ``color_encoding``/``prepare_color``), so
        # the edge color is passed as a constant ``mark_point`` property
        # rather than an encoding -- it never gets its own legend entry,
        # matching bokeh's/matplotlib's edge color (also never legended
        # separately from the fill color, see
        # ``plotmux.backends.bokeh.scatter.render_scatter``).
        kwargs.setdefault("filled", True)
        kwargs.setdefault(
            "stroke",
            rgba_to_altair(cast("tuple[float, float, float, float]", spec.edgecolor)),
        )
    if spec.fill is False:
        # ``mark_point(filled=False)`` is altair's own hollow-marker
        # spelling: the outline is drawn from ``color``/``stroke`` (an
        # unfilled point's own color acts as its stroke), matching every
        # other backend's "outline uses edgecolor, else color" fallback
        # (see ``ScatterSpec.fill``'s docstring). This overrides the
        # ``filled=True`` set above when ``edgecolor`` was also given --
        # ``fill=False`` wins, since a hollow marker has no fill to
        # distinguish from its stroke.
        kwargs["filled"] = False
    # ``MARKER_STYLE`` has no ``"x"`` entry (altair has no native "x" point
    # shape, see its docstring); ``.get`` leaves ``kwargs["shape"]`` unset
    # then, falling back to altair's own default shape (a circle), same as
    # ``spec.marker`` being unset.
    if spec.marker is not None and spec.marker in MARKER_STYLE:
        kwargs.setdefault("shape", MARKER_STYLE[spec.marker])
    data, encoding_color = prepare_color(data, spec.label, color, kwargs)
    chart = alt.Chart(alt.Data(values=data)).mark_point(**kwargs).encode(x="x:Q", y="y:Q")
    if encoding_color is not None:
        chart = chart.encode(color=encoding_color)
    return chart
