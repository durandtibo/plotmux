from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from plotmux.utils.imports import (
    check_plotly,
    is_plotly_available,
    plotly_available,
    raise_plotly_missing_error,
)

MODULE = "plotmux.utils.imports.plotly"


@pytest.fixture(autouse=True)
def _cache_clear() -> Generator[None]:
    is_plotly_available.cache_clear()
    yield
    is_plotly_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


#################################
#     Tests for check_plotly     #
#################################


def test_check_plotly_with_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: True):
        check_plotly()


def test_check_plotly_without_package() -> None:
    with (
        patch(f"{MODULE}.is_plotly_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'plotly' package is required but not installed."),
    ):
        check_plotly()


########################################
#     Tests for is_plotly_available     #
########################################


def test_is_plotly_available_returns_bool() -> None:
    assert isinstance(is_plotly_available(), bool)


def test_is_plotly_available_is_cached() -> None:
    with patch(f"{MODULE}.package_available", Mock(return_value=True)) as mock_package_available:
        is_plotly_available()
        is_plotly_available()
        assert mock_package_available.call_count == 1


#####################################
#     Tests for plotly_available     #
#####################################


def test_plotly_available_with_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: True):
        fn = plotly_available(my_function)
        assert fn(2) == 44


def test_plotly_available_without_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: False):
        fn = plotly_available(my_function)
        assert fn(2) is None


def test_plotly_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: True):

        @plotly_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_plotly_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: False):

        @plotly_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


###################################################
#     Tests for raise_plotly_missing_error     #
###################################################


def test_raise_plotly_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'plotly' package is required but not installed."):
        raise_plotly_missing_error()


def test_raise_plotly_missing_error_mentions_pip_install() -> None:
    with pytest.raises(RuntimeError, match=r"pip install plotly"):
        raise_plotly_missing_error()
