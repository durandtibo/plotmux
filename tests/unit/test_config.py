from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest

from plotmux.config import backend, get_default_backend, set_backend

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

##########################################
#     Tests for get_default_backend     #
##########################################


def test_get_default_backend_initial() -> None:
    assert get_default_backend() == "matplotlib"


@pytest.fixture
def _registered_fake_backend() -> Iterator[None]:
    from plotmux.backends.base import Backend
    from plotmux.backends.registry import _REGISTRY, register_backend

    class FakeBackend(Backend):
        name = "fake"

        def render(self, spec: Any, **kwargs: Any) -> Any:
            del kwargs
            return spec

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    snapshot = dict(_REGISTRY)
    register_backend(FakeBackend())
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


##################################
#     Tests for set_backend     #
##################################


def test_set_backend_updates_default() -> None:
    set_backend("xy")
    try:
        assert get_default_backend() == "xy"
    finally:
        set_backend("matplotlib")


def test_set_backend_returns_none() -> None:
    try:
        assert set_backend("xy") is None
    finally:
        set_backend("matplotlib")


@pytest.mark.usefixtures("_registered_fake_backend")
def test_set_backend_accepts_registered_but_non_builtin_name() -> None:
    set_backend("fake")
    try:
        assert get_default_backend() == "fake"
    finally:
        set_backend("matplotlib")


def test_set_backend_unknown_name_raises() -> None:
    with pytest.raises(RuntimeError, match="Unknown backend 'not_a_backend'"):
        set_backend("not_a_backend")


def test_set_backend_unknown_name_lists_known_backends() -> None:
    with pytest.raises(RuntimeError, match="matplotlib"):
        set_backend("not_a_backend")


def test_set_backend_unknown_name_lists_sorted_backends() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        set_backend("not_a_backend")
    from plotmux.backends.registry import known_backend_names

    available = sorted(known_backend_names())
    assert str(exc_info.value) == f"Unknown backend 'not_a_backend'. Known backends: {available}"


def test_set_backend_empty_string_raises() -> None:
    with pytest.raises(RuntimeError, match="Unknown backend ''"):
        set_backend("")


def test_set_backend_case_sensitive() -> None:
    with pytest.raises(RuntimeError, match="Unknown backend 'Matplotlib'"):
        set_backend("Matplotlib")


def test_set_backend_unknown_name_leaves_default_unchanged() -> None:
    assert get_default_backend() == "matplotlib"
    with pytest.raises(RuntimeError):
        set_backend("not_a_backend")
    assert get_default_backend() == "matplotlib"


def test_set_backend_accepts_entry_point_advertised_name() -> None:
    ep = Mock()
    ep.name = "plugin_backend"
    with patch("plotmux.backends.registry.entry_points", return_value=[ep]):
        set_backend("plugin_backend")
    try:
        assert get_default_backend() == "plugin_backend"
    finally:
        set_backend("matplotlib")


##############################
#     Tests for backend     #
##############################


def test_backend_context_manager_sets_backend() -> None:
    with backend("xy"):
        assert get_default_backend() == "xy"


def test_backend_context_manager_restores_previous() -> None:
    assert get_default_backend() == "matplotlib"
    with backend("xy"):
        assert get_default_backend() == "xy"
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_restores_on_error() -> None:
    assert get_default_backend() == "matplotlib"
    with pytest.raises(ValueError, match="boom"), backend("xy"):  # noqa: PT012
        msg = "boom"
        raise ValueError(msg)
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_nested() -> None:
    assert get_default_backend() == "matplotlib"
    with backend("xy"):
        assert get_default_backend() == "xy"
        with backend("altair"):
            assert get_default_backend() == "altair"
        assert get_default_backend() == "xy"
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_unknown_name_raises() -> None:
    assert get_default_backend() == "matplotlib"
    with pytest.raises(RuntimeError, match="Unknown backend"), backend("not_a_backend"):
        pass  # pragma: no cover
    assert get_default_backend() == "matplotlib"


def test_backend_context_manager_restores_nested_previous_on_inner_error() -> None:
    with backend("xy"):
        assert get_default_backend() == "xy"
        with pytest.raises(ValueError, match="boom"), backend("altair"):  # noqa: PT012
            msg = "boom"
            raise ValueError(msg)
        assert get_default_backend() == "xy"
    assert get_default_backend() == "matplotlib"
