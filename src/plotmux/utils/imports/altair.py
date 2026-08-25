r"""Contain utilities for optional altair dependency."""

from __future__ import annotations

__all__ = [
    "altair_available",
    "check_altair",
    "is_altair_available",
    "raise_altair_missing_error",
]

from functools import lru_cache
from typing import TYPE_CHECKING, Any, NoReturn, TypeVar

from coola.utils.imports.universal import (
    decorator_package_available,
    package_available,
    raise_package_missing_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable

F = TypeVar("F", bound="Callable[..., Any]")


def check_altair() -> None:
    r"""Check if the ``altair`` package is installed.

    Raises:
        RuntimeError: if the ``altair`` package is not installed.

    Example:
        ```pycon
        >>> from coola.utils.imports import check_altair
        >>> check_altair()

        ```
    """
    if not is_altair_available():
        raise_altair_missing_error()


@lru_cache(1)
def is_altair_available() -> bool:
    r"""Indicate if the ``altair`` package is installed or not.

    Returns:
        ``True`` if ``altair`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from coola.utils.imports import is_altair_available
        >>> is_altair_available()

        ```
    """
    return package_available("altair")


def altair_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``altair``
    is installed.

    Args:
        fn: The function to conditionally execute.

    Returns:
        A wrapper around ``fn`` if ``altair`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from coola.utils.imports import altair_available
        >>> @altair_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_altair_available)


def raise_altair_missing_error() -> NoReturn:
    r"""Raise a ``RuntimeError`` to indicate the ``altair`` package is
    missing.

    Raises:
        RuntimeError: Always, with a message indicating that the
            ``altair`` package is not installed.

    Example:
        ```pycon
        >>> from coola.utils.imports import raise_altair_missing_error
        >>> raise_altair_missing_error()  # doctest: +SKIP

        ```
    """
    raise_package_missing_error("altair", "altair")
