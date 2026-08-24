from __future__ import annotations

import pytest

from plotmux.testing.fixtures import (
    matplotlib_available,
    matplotlib_not_available,
    xy_available,
    xy_not_available,
)
from plotmux.utils.imports import is_matplotlib_available, is_xy_available


def test_matplotlib_available_is_mark_decorator() -> None:
    assert isinstance(matplotlib_available, pytest.MarkDecorator)


def test_matplotlib_not_available_is_mark_decorator() -> None:
    assert isinstance(matplotlib_not_available, pytest.MarkDecorator)


def test_xy_available_is_mark_decorator() -> None:
    assert isinstance(xy_available, pytest.MarkDecorator)


def test_xy_not_available_is_mark_decorator() -> None:
    assert isinstance(xy_not_available, pytest.MarkDecorator)


@matplotlib_available
def test_matplotlib_available_runs_when_matplotlib_installed() -> None:
    assert is_matplotlib_available()


@matplotlib_not_available
def test_matplotlib_not_available_runs_when_matplotlib_missing() -> None:
    assert not is_matplotlib_available()


@xy_available
def test_xy_available_runs_when_xy_installed() -> None:
    assert is_xy_available()


@xy_not_available
def test_xy_not_available_runs_when_xy_missing() -> None:
    assert not is_xy_available()
