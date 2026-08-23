from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from plotmux.utils.imports import (
    check_xy,
    is_xy_available,
    raise_xy_missing_error,
    xy_available,
)

logger = logging.getLogger(__name__)

MODULE = "plotmux.utils.imports.xy"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_xy_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


##############
#     xy     #
##############


def test_check_xy_with_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: True):
        check_xy()


def test_check_xy_without_package() -> None:
    with (
        patch(f"{MODULE}.is_xy_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'xy' package is required but not installed."),
    ):
        check_xy()


def test_is_xy_available() -> None:
    assert isinstance(is_xy_available(), bool)


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


def test_raise_xy_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'xy' package is required but not installed."):
        raise_xy_missing_error()
