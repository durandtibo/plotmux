r"""Contain the availability checks of the optional backend libraries.

``is_<package>_available`` indicates if a library can be imported and
``check_<package>`` raises a ``MissingPackageError`` if it cannot.
"""

from __future__ import annotations

__all__ = [
    "check_altair",
    "check_bokeh",
    "check_matplotlib",
    "check_plotly",
    "check_xy",
    "is_altair_available",
    "is_bokeh_available",
    "is_matplotlib_available",
    "is_plotly_available",
    "is_xy_available",
]

from coola.utils.imports import (
    availability_cache,
    module_available,
    raise_package_missing_error,
)


@availability_cache
def is_altair_available() -> bool:
    r"""Indicate if the ``altair`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``altair`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_altair_available
        >>> is_altair_available()

        ```
    """
    return module_available("altair")


def check_altair() -> None:
    r"""Check if the ``altair`` package is installed.

    Raises:
        MissingPackageError: if the ``altair`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_altair
        >>> check_altair()

        ```
    """
    if not is_altair_available():
        raise_package_missing_error("altair")


@availability_cache
def is_bokeh_available() -> bool:
    r"""Indicate if the ``bokeh`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``bokeh`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_bokeh_available
        >>> is_bokeh_available()

        ```
    """
    return module_available("bokeh")


def check_bokeh() -> None:
    r"""Check if the ``bokeh`` package is installed.

    Raises:
        MissingPackageError: if the ``bokeh`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_bokeh
        >>> check_bokeh()

        ```
    """
    if not is_bokeh_available():
        raise_package_missing_error("bokeh")


@availability_cache
def is_matplotlib_available() -> bool:
    r"""Indicate if the ``matplotlib`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``matplotlib`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_matplotlib_available
        >>> is_matplotlib_available()

        ```
    """
    return module_available("matplotlib")


def check_matplotlib() -> None:
    r"""Check if the ``matplotlib`` package is installed.

    Raises:
        MissingPackageError: if the ``matplotlib`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_matplotlib
        >>> check_matplotlib()

        ```
    """
    if not is_matplotlib_available():
        raise_package_missing_error("matplotlib")


@availability_cache
def is_plotly_available() -> bool:
    r"""Indicate if the ``plotly`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``plotly`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_plotly_available
        >>> is_plotly_available()

        ```
    """
    return module_available("plotly")


def check_plotly() -> None:
    r"""Check if the ``plotly`` package is installed.

    Raises:
        MissingPackageError: if the ``plotly`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_plotly
        >>> check_plotly()

        ```
    """
    if not is_plotly_available():
        raise_package_missing_error("plotly")


@availability_cache
def is_xy_available() -> bool:
    r"""Indicate if the ``xy`` package is installed and can be
    imported.

    Returns:
        ``True`` if ``xy`` is available otherwise ``False``.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import is_xy_available
        >>> is_xy_available()

        ```
    """
    return module_available("xy")


def check_xy() -> None:
    r"""Check if the ``xy`` package is installed.

    Raises:
        MissingPackageError: if the ``xy`` package is not installed.

    Example:
        ```pycon
        >>> from plotmux.utils.imports import check_xy
        >>> check_xy()

        ```
    """
    if not is_xy_available():
        raise_package_missing_error("xy")
