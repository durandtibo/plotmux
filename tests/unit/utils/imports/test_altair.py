from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from plotmux.utils.imports import (
    altair_available,
    check_altair,
    is_altair_available,
    raise_altair_missing_error,
)

MODULE = "plotmux.utils.imports.altair"


@pytest.fixture(autouse=True)
def _cache_clear() -> Generator[None]:
    is_altair_available.cache_clear()
    yield
    is_altair_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


#################################
#     Tests for check_altair     #
#################################


def test_check_altair_with_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: True):
        check_altair()


def test_check_altair_without_package() -> None:
    with (
        patch(f"{MODULE}.is_altair_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'altair' package is required but not installed."),
    ):
        check_altair()


#######################################
#     Tests for is_altair_available     #
#######################################


def test_is_altair_available_returns_bool() -> None:
    assert isinstance(is_altair_available(), bool)


def test_is_altair_available_is_cached() -> None:
    with patch(f"{MODULE}.package_available", Mock(return_value=True)) as mock_package_available:
        is_altair_available()
        is_altair_available()
        assert mock_package_available.call_count == 1


#####################################
#     Tests for altair_available     #
#####################################


def test_altair_available_with_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: True):
        fn = altair_available(my_function)
        assert fn(2) == 44


def test_altair_available_without_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: False):
        fn = altair_available(my_function)
        assert fn(2) is None


def test_altair_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: True):

        @altair_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_altair_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: False):

        @altair_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


###################################################
#     Tests for raise_altair_missing_error     #
###################################################


def test_raise_altair_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'altair' package is required but not installed."):
        raise_altair_missing_error()


def test_raise_altair_missing_error_mentions_pip_install() -> None:
    with pytest.raises(RuntimeError, match=r"pip install altair"):
        raise_altair_missing_error()
