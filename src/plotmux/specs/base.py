r"""Contain the base class for backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = ["BaseSpec"]

# ``_check_equal_length`` is a module-level helper, not a method on
# ``BaseSpec``: unlike color, not every spec has an x/y pair (e.g.
# ``HistogramSpec`` has neither), so it does not belong on the shared base
# class the way ``_normalize_color`` does.

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from plotmux.colors import parse_color
from plotmux.exceptions import InvalidSpecError

if TYPE_CHECKING:
    import numpy as np


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

    def _normalize_color(self, name: str = "color") -> None:
        r"""Normalize a ``str | tuple | None`` color field to its
        canonical RGBA representation, in place.

        Every color-carrying spec (``HistogramSpec``, ``LineSpec``,
        ``ScatterSpec``, ...) repeats the same two lines in its own
        ``__post_init__``: parse the field via ``parse_color`` and
        write it back with ``object.__setattr__`` (required because
        specs are frozen dataclasses). Factored here once so a new
        color-carrying spec only has to call
        ``self._normalize_color()`` from its own ``__post_init__``
        rather than reimplementing this.

        A field value of ``None`` is left untouched: it means "use
        the backend's default color" and is meaningful on its own,
        not something to normalize.

        Args:
            name: The name of the color field to normalize. Defaults
                to ``"color"``, the name used by every current
                color-carrying spec.

        Raises:
            ValueError: if the field's value is not a valid color.
        """
        value = getattr(self, name)
        if value is not None:
            object.__setattr__(self, name, parse_color(value))


def _check_equal_length(x: np.ndarray, y: np.ndarray) -> None:
    r"""Check that ``x`` and ``y`` have the same length.

    Shared by every spec that pairs an ``x`` array with a ``y`` array
    (``LineSpec``, ``ScatterSpec``, ...), so the check and its error
    message are written once.

    Args:
        x: The array of x values.
        y: The array of y values.

    Raises:
        InvalidSpecError: if ``x`` and ``y`` do not have the same
            length. Also a ``ValueError``, so existing ``except
            ValueError`` code keeps working unchanged.
    """
    if x.ndim != 1 or y.ndim != 1:
        msg = f"x and y must be 1-dimensional, but received shapes {x.shape} and {y.shape}"
        raise InvalidSpecError(msg)
    if x.shape[0] != y.shape[0]:
        msg = f"x and y must have the same length, but received {x.shape[0]} and {y.shape[0]}"
        raise InvalidSpecError(msg)
