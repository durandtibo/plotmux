from __future__ import annotations

import pytest

from plotmux.config import backend, get_default_backend, set_backend

##########################################
#     Tests for get_default_backend     #
##########################################


def test_get_default_backend_initial() -> None:
    assert get_default_backend() == "matplotlib"


##################################
#     Tests for set_backend     #
##################################


def test_set_backend_updates_default() -> None:
    set_backend("fake")
    try:
        assert get_default_backend() == "fake"
    finally:
        set_backend("matplotlib")


def test_set_backend_returns_none() -> None:
    try:
        assert set_backend("fake") is None
    finally:
        set_backend("matplotlib")


##############################
#     Tests for backend     #
##############################


def test_backend_context_manager_sets_backend() -> None:
    with backend("fake"):
        assert get_default_backend() == "fake"


def test_backend_context_manager_restores_previous() -> None:
    assert get_default_backend() == "matplotlib"
    with backend("fake"):
        assert get_default_backend() == "fake"
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_restores_on_error() -> None:
    assert get_default_backend() == "matplotlib"
    with pytest.raises(ValueError, match="boom"), backend("fake"):  # noqa: PT012
        msg = "boom"
        raise ValueError(msg)
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_nested() -> None:
    assert get_default_backend() == "matplotlib"
    with backend("outer"):
        assert get_default_backend() == "outer"
        with backend("inner"):
            assert get_default_backend() == "inner"
        assert get_default_backend() == "outer"
    assert get_default_backend() == "matplotlib"
