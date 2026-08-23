r"""Contain the default-backend configuration."""

from __future__ import annotations

__all__ = ["backend", "get_default_backend", "set_backend"]

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_DEFAULT_BACKEND = "matplotlib"


def set_backend(name: str) -> None:
    r"""Set the process-wide default backend.

    Args:
        name: The name of the backend to use by default, e.g.
            ``"matplotlib"``.

    Example:
        ```pycon
        >>> import plotmux
        >>> plotmux.set_backend("matplotlib")

        ```
    """
    global _DEFAULT_BACKEND  # noqa: PLW0603
    _DEFAULT_BACKEND = name


def get_default_backend() -> str:
    r"""Get the name of the current default backend.

    Returns:
        The name of the current default backend.
    """
    return _DEFAULT_BACKEND


@contextmanager
def backend(name: str) -> Iterator[None]:
    r"""Temporarily override the default backend.

    Args:
        name: The name of the backend to use within the ``with``
            block.

    Yields:
        Nothing. Restores the previous default backend on exit.

    Example:
        ```pycon
        >>> import plotmux
        >>> with plotmux.backend("matplotlib"):
        ...     fig = plotmux.hist([1, 2, 3])
        ...

        ```
    """
    previous = get_default_backend()
    set_backend(name)
    try:
        yield
    finally:
        set_backend(previous)
