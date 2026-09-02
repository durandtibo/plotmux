from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest

from plotmux.backends.base import Backend
from plotmux.backends.registry import (
    _REGISTRY,
    ENTRY_POINT_GROUP,
    get_backend,
    load_entry_point_backends,
    register_backend,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class FakeBackend(Backend):
    name = "fake"

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        del native, path, fmt


@pytest.fixture(autouse=True)
def _restore_registry() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


######################################
#     Tests for register_backend     #
######################################


def test_register_and_get_backend() -> None:
    register_backend(FakeBackend())
    assert isinstance(get_backend("fake"), FakeBackend)


def test_register_backend_replaces_existing() -> None:
    register_backend(FakeBackend())
    second = FakeBackend()
    register_backend(second)
    assert get_backend("fake") is second


def test_register_backend_under_own_name() -> None:
    class OtherNameBackend(Backend):
        name = "other"

        def render(self, spec: Any, **kwargs: Any) -> Any:
            del kwargs
            return spec

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    register_backend(OtherNameBackend())
    assert "other" in _REGISTRY


##################################
#     Tests for get_backend     #
##################################


def test_get_backend_missing() -> None:
    with pytest.raises(RuntimeError, match="No backend registered under the name 'missing'"):
        get_backend("missing")


def test_get_backend_missing_lists_available() -> None:
    _REGISTRY.clear()
    register_backend(FakeBackend())
    with pytest.raises(RuntimeError, match=r"Available backends: \['fake'\]"):
        get_backend("missing")


def test_get_backend_lazily_imports_builtin_backend_module() -> None:
    # A built-in backend name (e.g. "matplotlib") not yet in ``_REGISTRY``
    # is resolved by importing its submodule on first request, rather than
    # raising immediately. ``importlib.import_module`` is mocked (instead
    # of actually popping the already-imported submodule from
    # ``_REGISTRY``/``sys.modules``) since re-importing an already-imported
    # module is a no-op that would not re-run its registration side effect.
    _REGISTRY.pop("matplotlib", None)

    class FakeMatplotlibBackend(FakeBackend):
        name = "matplotlib"

    with patch("plotmux.backends.registry.importlib.import_module") as mock_import:
        mock_import.side_effect = lambda _name: register_backend(FakeMatplotlibBackend())
        backend = get_backend("matplotlib")
    mock_import.assert_called_once_with("plotmux.backends.matplotlib")
    assert isinstance(backend, FakeMatplotlibBackend)


##############################################
#     Tests for load_entry_point_backends     #
##############################################


def test_load_entry_point_backends_queries_own_group() -> None:
    with patch("plotmux.backends.registry.entry_points", return_value=[]) as mock_entry_points:
        load_entry_point_backends()
    mock_entry_points.assert_called_once_with(group=ENTRY_POINT_GROUP)


def test_load_entry_point_backends_loads_each_entry_point() -> None:
    ep1, ep2 = Mock(), Mock()
    with patch("plotmux.backends.registry.entry_points", return_value=[ep1, ep2]):
        load_entry_point_backends()
    ep1.load.assert_called_once_with()
    ep2.load.assert_called_once_with()


def test_load_entry_point_backends_suppresses_import_error() -> None:
    broken = Mock()
    broken.load.side_effect = ImportError("underlying library not installed")
    with patch("plotmux.backends.registry.entry_points", return_value=[broken]):
        load_entry_point_backends()  # must not raise
    broken.load.assert_called_once_with()


def test_load_entry_point_backends_one_broken_does_not_block_others() -> None:
    broken = Mock()
    broken.load.side_effect = ImportError
    ok = Mock()
    with patch("plotmux.backends.registry.entry_points", return_value=[broken, ok]):
        load_entry_point_backends()
    ok.load.assert_called_once_with()


def test_load_entry_point_backends_warns_on_non_import_error() -> None:
    broken = Mock()
    broken.name = "broken"
    broken.value = "broken.module"
    broken.load.side_effect = AttributeError("boom")
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[broken]),
        pytest.warns(RuntimeWarning, match="broken"),
    ):
        load_entry_point_backends()  # must not raise
    broken.load.assert_called_once_with()


def test_load_entry_point_backends_non_import_error_does_not_block_others() -> None:
    broken = Mock()
    broken.name = "broken"
    broken.value = "broken.module"
    broken.load.side_effect = RuntimeError("boom")
    ok = Mock()
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[broken, ok]),
        pytest.warns(RuntimeWarning),
    ):
        load_entry_point_backends()
    ok.load.assert_called_once_with()
