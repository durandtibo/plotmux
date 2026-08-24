from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from plotmux.utils.imports import (
    check_xy,
    is_xy_available,
    raise_xy_missing_error,
    xy_available,
)

MODULE = "plotmux.utils.imports.xy"


@pytest.fixture(autouse=True)
def _cache_clear() -> Generator[None]:
    is_xy_available.cache_clear()
    yield
    is_xy_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


############################
#     Tests for check_xy     #
############################


def test_check_xy_with_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: True):
        check_xy()


def test_check_xy_without_package() -> None:
    with (
        patch(f"{MODULE}.is_xy_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'xy' package is required but not installed."),
    ):
        check_xy()


##################################
#     Tests for is_xy_available     #
##################################


def test_is_xy_available_returns_bool() -> None:
    assert isinstance(is_xy_available(), bool)


def test_is_xy_available_is_cached() -> None:
    with patch(f"{MODULE}.package_available", Mock(return_value=True)) as mock_package_available:
        is_xy_available()
        is_xy_available()
        assert mock_package_available.call_count == 1


################################
#     Tests for xy_available     #
################################


def test_xy_available_with_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: True):
        fn = xy_available(my_function)
        assert fn(2) == 44


def test_xy_available_without_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: False):
        fn = xy_available(my_function)
        assert fn(2) is None


def test_xy_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: True):

        @xy_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_xy_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: False):

        @xy_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


##############################################
#     Tests for raise_xy_missing_error     #
##############################################


def test_raise_xy_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'xy' package is required but not installed."):
        raise_xy_missing_error()


def test_raise_xy_missing_error_mentions_pip_install() -> None:
    with pytest.raises(RuntimeError, match=r"pip install xy"):
        raise_xy_missing_error()
