from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from plotmux.utils.imports import (
    check_matplotlib,
    is_matplotlib_available,
    matplotlib_available,
    raise_matplotlib_missing_error,
)

MODULE = "plotmux.utils.imports.matplotlib"


@pytest.fixture(autouse=True)
def _cache_clear() -> Generator[None]:
    is_matplotlib_available.cache_clear()
    yield
    is_matplotlib_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


#####################################
#     Tests for check_matplotlib     #
#####################################


def test_check_matplotlib_with_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: True):
        check_matplotlib()


def test_check_matplotlib_without_package() -> None:
    with (
        patch(f"{MODULE}.is_matplotlib_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'matplotlib' package is required but not installed."),
    ):
        check_matplotlib()


##########################################
#     Tests for is_matplotlib_available     #
##########################################


def test_is_matplotlib_available_returns_bool() -> None:
    assert isinstance(is_matplotlib_available(), bool)


def test_is_matplotlib_available_is_cached() -> None:
    with patch(f"{MODULE}.package_available", Mock(return_value=True)) as mock_package_available:
        is_matplotlib_available()
        is_matplotlib_available()
        assert mock_package_available.call_count == 1


#########################################
#     Tests for matplotlib_available     #
#########################################


def test_matplotlib_available_with_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: True):
        fn = matplotlib_available(my_function)
        assert fn(2) == 44


def test_matplotlib_available_without_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: False):
        fn = matplotlib_available(my_function)
        assert fn(2) is None


def test_matplotlib_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: True):

        @matplotlib_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_matplotlib_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: False):

        @matplotlib_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


####################################################
#     Tests for raise_matplotlib_missing_error     #
####################################################


def test_raise_matplotlib_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'matplotlib' package is required but not installed."):
        raise_matplotlib_missing_error()


def test_raise_matplotlib_missing_error_mentions_pip_install() -> None:
    with pytest.raises(RuntimeError, match=r"pip install matplotlib"):
        raise_matplotlib_missing_error()
