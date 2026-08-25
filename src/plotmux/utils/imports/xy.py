r"""Contain utilities for optional xy dependency."""

from __future__ import annotations

__all__ = [
    "check_xy",
    "is_xy_available",
    "raise_xy_missing_error",
    "xy_available",
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


def check_xy() -> None:
    r"""Check if the ``xy`` package is installed.

    Raises:
        RuntimeError: if the ``xy`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_xy
        >>> check_xy()

        ```
    """
    if not is_xy_available():
        raise_xy_missing_error()


@lru_cache(1)
def is_xy_available() -> bool:
    r"""Indicate if the ``xy`` package is installed or not.

    Returns:
        ``True`` if ``xy`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_xy_available
        >>> is_xy_available()

        ```
    """
    return package_available("xy")


def xy_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``xy``
    is installed.

    Args:
        fn: The function to conditionally execute.

    Returns:
        A wrapper around ``fn`` if ``xy`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import xy_available
        >>> @xy_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_xy_available)


def raise_xy_missing_error() -> NoReturn:
    r"""Raise a ``RuntimeError`` to indicate the ``xy`` package is
    missing.

    Raises:
        RuntimeError: Always, with a message indicating that the
            ``xy`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import raise_xy_missing_error
        >>> raise_xy_missing_error()  # doctest: +SKIP

        ```
    """
    raise_package_missing_error("xy", "xy")
