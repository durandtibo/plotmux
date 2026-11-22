r"""Contain generic helpers to detect optional dependencies."""

from __future__ import annotations

__all__ = ["decorator_package_available"]

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


def decorator_package_available(
    fn: Callable[P, R], condition: Callable[[], bool]
) -> Callable[P, R | None]:
    r"""Implement a decorator to execute a function only if a package
    is installed.

    Args:
        fn: The function to conditionally execute.
        condition: A callable without argument that returns ``True``
            if the package is available, otherwise ``False``.

    Returns:
        A wrapper around ``fn`` if ``condition()`` is ``True``,
            otherwise a function that does nothing and returns
            ``None``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports.package import decorator_package_available
        >>> def my_function(n: int = 0) -> int:
        ...     return 42 + n
        ...
        >>> decorator_package_available(my_function, lambda: True)()
        42
        >>> decorator_package_available(my_function, lambda: False)() is None
        True

        ```
    """

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        if condition():
            return fn(*args, **kwargs)
        return None

    return wrapper
