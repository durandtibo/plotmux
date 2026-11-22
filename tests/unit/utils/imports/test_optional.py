from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from plotmux.utils.imports import MissingPackageError, clear_availability_caches
from plotmux.utils.imports.optional import (
    check_altair,
    check_bokeh,
    check_matplotlib,
    check_plotly,
    check_xy,
    is_altair_available,
    is_bokeh_available,
    is_matplotlib_available,
    is_plotly_available,
    is_xy_available,
)

if TYPE_CHECKING:
    from collections.abc import Generator

MODULE = "plotmux.utils.imports.optional"


@pytest.fixture(autouse=True)
def _clear_caches() -> Generator[None]:
    clear_availability_caches()
    yield
    clear_availability_caches()


############################
#     Tests for altair     #
############################


def test_is_altair_available_returns_bool() -> None:
    assert isinstance(is_altair_available(), bool)


def test_is_altair_available_true() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        assert is_altair_available()
        mock.assert_called_once_with("altair")


def test_is_altair_available_false() -> None:
    with patch(f"{MODULE}.module_available", return_value=False):
        assert not is_altair_available()


def test_is_altair_available_is_cached() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        is_altair_available()
        is_altair_available()
        assert mock.call_count == 1


def test_check_altair_with_package() -> None:
    with patch(f"{MODULE}.is_altair_available", lambda: True):
        check_altair()


def test_check_altair_without_package() -> None:
    with (
        patch(f"{MODULE}.is_altair_available", lambda: False),
        pytest.raises(
            MissingPackageError, match=r"'altair' package is required but not installed."
        ),
    ):
        check_altair()


###########################
#     Tests for bokeh     #
###########################


def test_is_bokeh_available_returns_bool() -> None:
    assert isinstance(is_bokeh_available(), bool)


def test_is_bokeh_available_true() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        assert is_bokeh_available()
        mock.assert_called_once_with("bokeh")


def test_is_bokeh_available_false() -> None:
    with patch(f"{MODULE}.module_available", return_value=False):
        assert not is_bokeh_available()


def test_is_bokeh_available_is_cached() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        is_bokeh_available()
        is_bokeh_available()
        assert mock.call_count == 1


def test_check_bokeh_with_package() -> None:
    with patch(f"{MODULE}.is_bokeh_available", lambda: True):
        check_bokeh()


def test_check_bokeh_without_package() -> None:
    with (
        patch(f"{MODULE}.is_bokeh_available", lambda: False),
        pytest.raises(MissingPackageError, match=r"'bokeh' package is required but not installed."),
    ):
        check_bokeh()


################################
#     Tests for matplotlib     #
################################


def test_is_matplotlib_available_returns_bool() -> None:
    assert isinstance(is_matplotlib_available(), bool)


def test_is_matplotlib_available_true() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        assert is_matplotlib_available()
        mock.assert_called_once_with("matplotlib")


def test_is_matplotlib_available_false() -> None:
    with patch(f"{MODULE}.module_available", return_value=False):
        assert not is_matplotlib_available()


def test_is_matplotlib_available_is_cached() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        is_matplotlib_available()
        is_matplotlib_available()
        assert mock.call_count == 1


def test_check_matplotlib_with_package() -> None:
    with patch(f"{MODULE}.is_matplotlib_available", lambda: True):
        check_matplotlib()


def test_check_matplotlib_without_package() -> None:
    with (
        patch(f"{MODULE}.is_matplotlib_available", lambda: False),
        pytest.raises(
            MissingPackageError, match=r"'matplotlib' package is required but not installed."
        ),
    ):
        check_matplotlib()


############################
#     Tests for plotly     #
############################


def test_is_plotly_available_returns_bool() -> None:
    assert isinstance(is_plotly_available(), bool)


def test_is_plotly_available_true() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        assert is_plotly_available()
        mock.assert_called_once_with("plotly")


def test_is_plotly_available_false() -> None:
    with patch(f"{MODULE}.module_available", return_value=False):
        assert not is_plotly_available()


def test_is_plotly_available_is_cached() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        is_plotly_available()
        is_plotly_available()
        assert mock.call_count == 1


def test_check_plotly_with_package() -> None:
    with patch(f"{MODULE}.is_plotly_available", lambda: True):
        check_plotly()


def test_check_plotly_without_package() -> None:
    with (
        patch(f"{MODULE}.is_plotly_available", lambda: False),
        pytest.raises(
            MissingPackageError, match=r"'plotly' package is required but not installed."
        ),
    ):
        check_plotly()


########################
#     Tests for xy     #
########################


def test_is_xy_available_returns_bool() -> None:
    assert isinstance(is_xy_available(), bool)


def test_is_xy_available_true() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        assert is_xy_available()
        mock.assert_called_once_with("xy")


def test_is_xy_available_false() -> None:
    with patch(f"{MODULE}.module_available", return_value=False):
        assert not is_xy_available()


def test_is_xy_available_is_cached() -> None:
    with patch(f"{MODULE}.module_available", return_value=True) as mock:
        is_xy_available()
        is_xy_available()
        assert mock.call_count == 1


def test_check_xy_with_package() -> None:
    with patch(f"{MODULE}.is_xy_available", lambda: True):
        check_xy()


def test_check_xy_without_package() -> None:
    with (
        patch(f"{MODULE}.is_xy_available", lambda: False),
        pytest.raises(MissingPackageError, match=r"'xy' package is required but not installed."),
    ):
        check_xy()
