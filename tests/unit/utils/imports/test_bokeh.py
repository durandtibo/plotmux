from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from plotmux.utils.imports import (
    bokeh_available,
    check_bokeh,
    is_bokeh_available,
    raise_bokeh_missing_error,
)

MODULE = "plotmux.utils.imports.bokeh"


@pytest.fixture(autouse=True)
def _cache_clear() -> Generator[None]:
    is_bokeh_available.cache_clear()
    yield
    is_bokeh_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


################################
#     Tests for check_bokeh     #
################################


def test_check_bokeh_with_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: True):
        check_bokeh()


def test_check_bokeh_without_package() -> None:
    with (
        patch(f"{MODULE}.is_bokeh_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'bokeh' package is required but not installed."),
    ):
        check_bokeh()


######################################
#     Tests for is_bokeh_available     #
######################################


def test_is_bokeh_available_returns_bool() -> None:
    assert isinstance(is_bokeh_available(), bool)


def test_is_bokeh_available_is_cached() -> None:
    with patch(f"{MODULE}.package_available", Mock(return_value=True)) as mock_package_available:
        is_bokeh_available()
        is_bokeh_available()
        assert mock_package_available.call_count == 1


####################################
#     Tests for bokeh_available     #
####################################


def test_bokeh_available_with_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: True):
        fn = bokeh_available(my_function)
        assert fn(2) == 44


def test_bokeh_available_without_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: False):
        fn = bokeh_available(my_function)
        assert fn(2) is None


def test_bokeh_available_decorator_with_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: True):

        @bokeh_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) == 44


def test_bokeh_available_decorator_without_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: False):

        @bokeh_available
        def fn(n: int = 0) -> int:
            return 42 + n

        assert fn(2) is None


##################################################
#     Tests for raise_bokeh_missing_error     #
##################################################


def test_raise_bokeh_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'bokeh' package is required but not installed."):
        raise_bokeh_missing_error()


def test_raise_bokeh_missing_error_mentions_pip_install() -> None:
    with pytest.raises(RuntimeError, match=r"pip install bokeh"):
        raise_bokeh_missing_error()
