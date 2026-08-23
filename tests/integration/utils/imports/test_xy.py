from __future__ import annotations

import logging

import pytest

from plotmux.testing.fixtures import xy_available, xy_not_available
from plotmux.utils.imports import check_xy, is_xy_available

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


@xy_available
def test_check_xy_with_package() -> None:
    check_xy()


@xy_not_available
def test_check_xy_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'xy' package is required but not installed."):
        check_xy()


@xy_available
def test_is_xy_available_true() -> None:
    assert is_xy_available()


@xy_not_available
def test_is_xy_available_false() -> None:
    assert not is_xy_available()
