r"""Contain utilities for optional bokeh dependency."""

from __future__ import annotations

__all__ = [
    "bokeh_available",
    "check_bokeh",
    "is_bokeh_available",
    "raise_bokeh_missing_error",
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


def check_bokeh() -> None:
    r"""Check if the ``bokeh`` package is installed.

    Raises:
        RuntimeError: if the ``bokeh`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_bokeh
        >>> check_bokeh()

        ```
    """
    if not is_bokeh_available():
        raise_bokeh_missing_error()


@lru_cache(1)
def is_bokeh_available() -> bool:
    r"""Indicate if the ``bokeh`` package is installed or not.

    Returns:
        ``True`` if ``bokeh`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_bokeh_available
        >>> is_bokeh_available()

        ```
    """
    return package_available("bokeh")


def bokeh_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``bokeh``
    is installed.

    Args:
        fn: The function to conditionally execute.

    Returns:
        A wrapper around ``fn`` if ``bokeh`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import bokeh_available
        >>> @bokeh_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_bokeh_available)


def raise_bokeh_missing_error() -> NoReturn:
    r"""Raise a ``RuntimeError`` to indicate the ``bokeh`` package is
    missing.

    Raises:
        RuntimeError: Always, with a message indicating that the
            ``bokeh`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import raise_bokeh_missing_error
        >>> raise_bokeh_missing_error()  # doctest: +SKIP

        ```
    """
    raise_package_missing_error("bokeh", "bokeh")
