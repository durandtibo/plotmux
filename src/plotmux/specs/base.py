r"""Contain the base class for backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = ["BaseSpec"]

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class BaseSpec:
    r"""Define the base class for chart specifications.

    A spec is a plain, backend-agnostic description of *what* to
    plot (data + encoding + style). It must never import or hold a
    reference to a plotting library object. Turning a spec into a
    native figure is the responsibility of a backend (see
    ``plotmux.backends``).

    Subclasses are expected to be frozen dataclasses and may use
    ``__post_init__`` to validate their fields.

    Args:
        title: An optional figure title.
        xlabel: An optional x-axis label.
        ylabel: An optional y-axis label.
        xscale: The x-axis scale, ``"linear"`` or ``"log"``.
        yscale: The y-axis scale, ``"linear"`` or ``"log"``.

    These are figure-level concerns shared by every chart type, so
    they live here rather than being redeclared per chart type. Every
    backend applies them the same way, in one shared
    ``apply_common_style`` helper, right after drawing the
    chart-specific mark (see e.g.
    ``plotmux.backends.matplotlib.style.apply_common_style``).
    Unlike ``title``/``xlabel``/``ylabel``, ``xscale``/``yscale``
    default to ``"linear"`` rather than ``None``: an axis always has
    *some* scale, so there is no meaningful "unset" state to skip.
    """

    # ``kw_only=True`` so these figure-level fields (all defaulted) can
    # precede a subclass's own required fields (e.g. ``HistogramSpec.values``)
    # without violating the dataclass "no non-default field after a default
    # field" rule -- callers already pass them by keyword (`plotmux.hist(...,
    # title=...)`), so this changes no call site.
    title: str | None = field(default=None, kw_only=True)
    xlabel: str | None = field(default=None, kw_only=True)
    ylabel: str | None = field(default=None, kw_only=True)
    xscale: Literal["linear", "log"] = field(default="linear", kw_only=True)
    yscale: Literal["linear", "log"] = field(default="linear", kw_only=True)
