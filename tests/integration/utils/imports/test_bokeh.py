from __future__ import annotations

import logging

import pytest

from plotmux.testing.fixtures import bokeh_available, bokeh_not_available
from plotmux.utils.imports import check_bokeh, is_bokeh_available

logger = logging.getLogger(__name__)

MODULE = "plotmux.utils.imports.bokeh"


@pytest.fixture(autouse=True)
def _cache_clear() -> None:
    is_bokeh_available.cache_clear()


def my_function(n: int = 0) -> int:
    return 42 + n


##################
#     bokeh     #
##################


@bokeh_available
def test_check_bokeh_with_package() -> None:
    check_bokeh()


@bokeh_not_available
def test_check_bokeh_without_package() -> None:
    with pytest.raises(RuntimeError, match=r"'bokeh' package is required but not installed."):
        check_bokeh()


@bokeh_available
def test_is_bokeh_available_true() -> None:
    assert is_bokeh_available()


@bokeh_not_available
def test_is_bokeh_available_false() -> None:
    assert not is_bokeh_available()
