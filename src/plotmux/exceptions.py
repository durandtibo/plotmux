r"""Contain plotmux's exception hierarchy.

Every exception plotmux itself raises is a ``PlotmuxError``, *in
addition to* whichever standard-library exception type the raise site
already documented (e.g. ``ValueError``, ``RuntimeError``). Each
concrete exception below multiply-inherits from both: ``except
ValueError`` (or ``RuntimeError``/``NotImplementedError``) at an
existing call site keeps working exactly as before, while new code can
catch anything plotmux-specific in one place with ``except
PlotmuxError``, without having to know or enumerate which builtin type
backs each individual error.

Only the exception *type* changes here, never the raised message or the
condition that triggers it -- this is purely an additive refinement of
what was already being raised.
"""

from __future__ import annotations

__all__ = [
    "BackendNotFoundError",
    "ExportError",
    "InvalidColorError",
    "InvalidSpecError",
    "PlotmuxError",
    "UnsupportedFormatError",
    "UnsupportedSpecError",
]


class PlotmuxError(Exception):
    r"""Base class for every exception raised by plotmux.

    Catch this to handle any plotmux-specific failure without having to
    know which of the more specific subclasses (or which builtin type
    each one also derives from) applies.
    """


class BackendNotFoundError(PlotmuxError, RuntimeError):
    r"""Raised when a backend name has no registered ``Backend``.

    Typically means the backend's underlying plotting library is not
    installed. See ``plotmux.backends.registry.get_backend``.
    """


class UnsupportedSpecError(PlotmuxError, NotImplementedError):
    r"""Raised when a backend has no renderer registered for a spec type.

    See ``plotmux.backends.base.resolve_renderer``.
    """


class UnsupportedFormatError(PlotmuxError, ValueError):
    r"""Raised when a backend does not support a requested export format.

    See ``plotmux.backends.base.check_export_format``.
    """


class InvalidColorError(PlotmuxError, ValueError):
    r"""Raised when a color value cannot be parsed.

    See ``plotmux.colors.parse_color``.
    """


class InvalidSpecError(PlotmuxError, ValueError):
    r"""Raised when a spec's field values fail validation.

    See each spec's ``__post_init__`` (e.g.
    ``plotmux.specs.HistogramSpec``, ``plotmux.specs.LineSpec``).
    """


class ExportError(PlotmuxError, ValueError):
    r"""Raised when a figure cannot be exported, other than an
    unsupported format.

    See ``plotmux.export.save``.
    """
