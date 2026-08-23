from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from plotmux.utils.imports import (
    check_matplotlib,
    is_matplotlib_available,
    matplotlib_available,
    raise_matplotlib_missing_error,
)

logger = logging.getLogger(__name__)

MODULE = "plotmux.utils.imports.matplotlib"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_matplotlib_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


######################
#     matplotlib     #
######################


def test_check_matplotlib_with_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: True):
        check_matplotlib()


def test_check_matplotlib_without_package() -> None:
    with (
        patch(f"{MODULE}.is_matplotlib_available", lambda: False),
        pytest.raises(RuntimeError, match=r"'matplotlib' package is required but not installed."),
    ):
        check_matplotlib()


def test_is_matplotlib_available() -> None:
    assert isinstance(is_matplotlib_available(), bool)


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


def test_raise_matplotlib_missing_error() -> None:
    with pytest.raises(RuntimeError, match=r"'matplotlib' package is required but not installed."):
        raise_matplotlib_missing_error()
