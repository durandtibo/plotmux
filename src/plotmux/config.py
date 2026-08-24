r"""Contain the default-backend configuration."""

from __future__ import annotations

__all__ = ["backend", "get_default_backend", "set_backend"]

from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# A ``ContextVar`` rather than a plain module global: it gives each thread
# and each ``asyncio`` task its own value, so ``set_backend``/``backend(...)``
# in one thread/task never leaks into or races with another one, while
# still behaving like a single process-wide default in the common
# single-threaded case.
_DEFAULT_BACKEND: ContextVar[str] = ContextVar("plotmux_default_backend", default="matplotlib")


def set_backend(name: str) -> None:
    r"""Set the default backend for the current thread/task.

    Args:
        name: The name of the backend to use by default, e.g.
            ``"matplotlib"``.

    Example:
        ```pycon
        >>> import plotmux
        >>> plotmux.set_backend("matplotlib")

        ```
    """
    _DEFAULT_BACKEND.set(name)


def get_default_backend() -> str:
    r"""Get the name of the current default backend.

    Returns:
        The name of the current default backend.
    """
    return _DEFAULT_BACKEND.get()


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
