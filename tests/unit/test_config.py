from __future__ import annotations

import pytest

from plotmux.config import backend, get_default_backend, set_backend


def test_get_default_backend_initial() -> None:
    assert get_default_backend() == "matplotlib"


def test_set_backend() -> None:
    set_backend("fake")
    try:
        assert get_default_backend() == "fake"
    finally:
        set_backend("matplotlib")


def test_backend_context_manager_restores_previous() -> None:
    assert get_default_backend() == "matplotlib"
    with backend("fake"):
        assert get_default_backend() == "fake"
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_restores_on_error() -> None:
    assert get_default_backend() == "matplotlib"
    with pytest.raises(ValueError, match="boom"), backend("fake"):
        raise ValueError("boom")  # noqa: EM101
    assert get_default_backend() == "matplotlib"
