r"""Contain figure export utilities."""

from __future__ import annotations

__all__ = ["save"]

from typing import TYPE_CHECKING

from coola.utils.path import sanitize_path

from plotmux.backends.base import check_export_format
from plotmux.backends.registry import get_backend
from plotmux.exceptions import ExportError

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.figure import Figure


def save(figure: Figure, path: str | Path) -> None:
    r"""Save a figure to a file.

    The export format is inferred from the file suffix (e.g.
    ``.png`` -> ``"png"``, ``.svg`` -> ``"svg"``).

    The parent directory of ``path`` is created if it does not
    already exist.

    Args:
        figure: The figure to save.
        path: The path where to save the figure.

    Raises:
        ExportError: if ``path`` has no suffix, so the export format
            cannot be inferred. Also a ``ValueError``, so existing
            ``except ValueError`` code keeps working unchanged.
        UnsupportedFormatError: if the backend does not support the
            inferred export format. See
            ``plotmux.backends.base.check_export_format``.
    """
    path = sanitize_path(path)
    fmt = path.suffix.lstrip(".").lower()
    if not fmt:
        msg = f"Cannot infer the export format from path {path!r}: it has no suffix"
        raise ExportError(msg)
    backend = get_backend(figure.backend_name)
    # Checked, and raised as ``UnsupportedFormatError`` -- the documented
    # exception type for this case (see ``plotmux.exceptions``) -- before
    # creating the parent directory: a backend's own ``save`` also calls
    # ``check_export_format`` before writing (see e.g.
    # ``plotmux.backends.matplotlib.backend.MatplotlibBackend.save``), but
    # this call must not depend on every backend (including a third-party
    # or test one) doing so itself, nor on that check's error type.
    # ``supported_formats`` is a required ``Backend`` attribute, but a
    # backend that declares none (e.g. a minimal test double) is treated as
    # accepting any format, rather than this raising an ``AttributeError``.
    supported = getattr(backend, "supported_formats", None)
    if supported is not None:
        check_export_format(fmt, supported, backend.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    backend.save(figure.native, path, fmt)
