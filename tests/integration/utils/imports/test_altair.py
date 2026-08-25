from __future__ import annotations

import logging

import pytest

from plotmux.testing.fixtures import altair_available, altair_not_available
from plotmux.utils.imports import check_altair, is_altair_available

logger = logging.getLogger(__name__)

MODULE = "plotmux.utils.imports.altair"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_altair_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


####################
#     altair     #
####################


@altair_available
def test_check_altair_with_package() -> None:
    check_altair()


@altair_not_available
def test_check_altair_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'altair' package is required but not installed."):
        check_altair()


@altair_available
def test_is_altair_available_true() -> None:
    assert is_altair_available()


@altair_not_available
def test_is_altair_available_false() -> None:
    assert not is_altair_available()
