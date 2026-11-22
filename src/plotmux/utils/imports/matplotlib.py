r"""Contain utilities for optional matplotlib dependency."""

from __future__ import annotations

__all__ = [
    "check_matplotlib",
    "is_matplotlib_available",
    "matplotlib_available",
    "raise_matplotlib_missing_error",
]

from functools import cache
from typing import TYPE_CHECKING, Never, ParamSpec, TypeVar

from coola.utils.imports import package_available, raise_package_missing_error

from plotmux.utils.imports.package import decorator_package_available

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


def check_matplotlib() -> None:
    r"""Check if the ``matplotlib`` package is installed.

    Raises:
        RuntimeError: if the ``matplotlib`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_matplotlib
        >>> check_matplotlib()

        ```
    """
    if not is_matplotlib_available():
        raise_matplotlib_missing_error()


@cache
def is_matplotlib_available() -> bool:
    r"""Indicate if the ``matplotlib`` package is installed or not.

    Returns:
        ``True`` if ``matplotlib`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_matplotlib_available
        >>> is_matplotlib_available()

        ```
    """
    return package_available("matplotlib")


def matplotlib_available(fn: Callable[P, R]) -> Callable[P, R | None]:
    r"""Implement a decorator to execute a function only if ``matplotlib``
    is installed.

    Args:
        fn: The function to conditionally execute.

    Returns:
        A wrapper around ``fn`` if ``matplotlib`` package is installed,
            otherwise ``None``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import matplotlib_available
        >>> @matplotlib_available
        ... def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> my_function()

        ```
    """
    return decorator_package_available(fn, is_matplotlib_available)


def raise_matplotlib_missing_error() -> Never:
    r"""Raise a ``RuntimeError`` to indicate the ``matplotlib`` package
    is missing.

    Raises:
        RuntimeError: Always, with a message indicating that the
            ``matplotlib`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import raise_matplotlib_missing_error
        >>> raise_matplotlib_missing_error()  # doctest: +SKIP

        ```
    """
    raise_package_missing_error("matplotlib", install="matplotlib")
