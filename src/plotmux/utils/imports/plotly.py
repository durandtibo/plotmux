r"""Contain utilities for optional plotly dependency."""

from __future__ import annotations

__all__ = [
    "check_plotly",
    "is_plotly_available",
    "plotly_available",
    "raise_plotly_missing_error",
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


def check_plotly() -> None:
    r"""Check if the ``plotly`` package is installed.

    Raises:
        RuntimeError: if the ``plotly`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_plotly
        >>> check_plotly()

        ```
    """
    if not is_plotly_available():
        raise_plotly_missing_error()


@lru_cache(1)
def is_plotly_available() -> bool:
    r"""Indicate if the ``plotly`` package is installed or not.

    Returns:
        ``True`` if ``plotly`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_plotly_available
        >>> is_plotly_available()

        ```
    """
    return package_available("plotly")


def plotly_available(fn: F) -> F:
    r"""Implement a decorator to execute a function only if ``plotly``
    is installed.

    Args:
        fn: The function to conditionally execute.

    Returns:
        A wrapper around ``fn`` if ``plotly`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import plotly_available
        >>> @plotly_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_plotly_available)


def raise_plotly_missing_error() -> NoReturn:
    r"""Raise a ``RuntimeError`` to indicate the ``plotly`` package is
    missing.

    Raises:
        RuntimeError: Always, with a message indicating that the
            ``plotly`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import raise_plotly_missing_error
        >>> raise_plotly_missing_error()  # doctest: +SKIP

        ```
    """
    raise_package_missing_error("plotly", "plotly")
