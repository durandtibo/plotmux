r"""Contain figure export utilities."""

from __future__ import annotations

__all__ = ["save"]

from typing import TYPE_CHECKING

from coola.utils.path import sanitize_path

from plotmux.backends.registry import get_backend

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
        ValueError: if ``path`` has no suffix, so the export format
            cannot be inferred.
    """
    path = sanitize_path(path)
    fmt = path.suffix.lstrip(".").lower()
    if not fmt:
        msg = f"Cannot infer the export format from path {path!r}: it has no suffix"
        raise ValueError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    backend = get_backend(figure.backend_name)
    backend.save(figure.native, path, fmt)
