from __future__ import annotations

import logging

import pytest

from plotmux.testing.fixtures import matplotlib_available, matplotlib_not_available
from plotmux.utils.imports import (
    MissingPackageError,
    check_matplotlib,
    clear_availability_caches,
    is_matplotlib_available,
)

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    clear_availability_caches()


def my_function(n: int = 0) -> int:
    return 42 + n


######################
#     matplotlib     #
######################


@matplotlib_available
def test_check_matplotlib_with_package() -> None:
    check_matplotlib()


@matplotlib_not_available
def test_check_matplotlib_without_package() -> None:
    with pytest.raises(
        MissingPackageError, match=r"'matplotlib' package is required but not installed."
    ):
        check_matplotlib()


@matplotlib_available
def test_is_matplotlib_available_true() -> None:
    assert is_matplotlib_available()


@matplotlib_not_available
def test_is_matplotlib_available_false() -> None:
    assert not is_matplotlib_available()
