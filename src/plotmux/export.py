r"""Contain figure export utilities."""

from __future__ import annotations

__all__ = ["save"]

from typing import TYPE_CHECKING

from coola.utils.path import sanitize_path

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
    """
    path = sanitize_path(path)
    fmt = path.suffix.lstrip(".").lower()
    if not fmt:
        msg = f"Cannot infer the export format from path {path!r}: it has no suffix"
        raise ExportError(msg)
    backend = get_backend(figure.backend_name)
    supported = getattr(backend, "supported_formats", None)
    if supported is not None and fmt not in supported:
        msg = (
            f"Unsupported export format {fmt!r} for backend {figure.backend_name!r}: "
            f"expected one of {sorted(supported)}"
        )
        raise ExportError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    backend.save(figure.native, path, fmt)
