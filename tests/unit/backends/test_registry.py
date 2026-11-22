from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast
from unittest.mock import Mock, patch

import pytest

from plotmux.backends.base import Backend
from plotmux.backends.registry import (
    _BUILTIN_AVAILABILITY,
    _BUILTIN_BACKENDS,
    _REGISTRY,
    ENTRY_POINT_GROUP,
    available_backends,
    capabilities,
    get_backend,
    known_backend_names,
    register_backend,
)
from plotmux.exceptions import BackendNotFoundError, BackendRegistrationError
from plotmux.testing.fixtures import (
    altair_available,
    bokeh_available,
    matplotlib_available,
    plotly_available,
    xy_available,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

BUILTIN_BACKENDS = [
    pytest.param("altair", marks=altair_available),
    pytest.param("bokeh", marks=bokeh_available),
    pytest.param("matplotlib", marks=matplotlib_available),
    pytest.param("plotly", marks=plotly_available),
    pytest.param("xy", marks=xy_available),
]


class FakeBackend(Backend):
    name = "fake"

    def render(self, spec: Any, **kwargs: Any) -> Any:
        del kwargs
        return spec

    def save(self, native: Any, path: Path, fmt: str) -> None:
        del native, path, fmt


class PluginBackend(FakeBackend):
    name = "plugin"


@pytest.fixture(autouse=True)
def _restore_registry() -> Iterator[None]:
    snapshot = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(snapshot)


def make_entry_point(value: Any, name: str = "plugin") -> Mock:
    entry_point = Mock()
    entry_point.name = name
    entry_point.value = "my_package.module:PluginBackend"
    entry_point.load.return_value = value
    return entry_point


######################################
#     Tests for register_backend     #
######################################


def test_register_and_get_backend() -> None:
    register_backend(FakeBackend())
    assert isinstance(get_backend("fake"), FakeBackend)


def test_register_backend_under_own_name() -> None:
    class OtherNameBackend(FakeBackend):
        name = "other"

    register_backend(OtherNameBackend())
    assert "other" in _REGISTRY


def test_register_backend_existing_name_raises() -> None:
    register_backend(FakeBackend())
    with pytest.raises(BackendRegistrationError, match="already registered under the name 'fake'"):
        register_backend(FakeBackend())


def test_register_backend_existing_name_is_kept_when_refused() -> None:
    first = FakeBackend()
    register_backend(first)
    with pytest.raises(BackendRegistrationError, match="replace=True"):
        register_backend(FakeBackend())
    assert get_backend("fake") is first


def test_register_backend_replace_existing() -> None:
    register_backend(FakeBackend())
    second = FakeBackend()
    register_backend(second, replace=True)
    assert get_backend("fake") is second


def test_register_backend_replace_a_name_not_used_yet() -> None:
    backend = FakeBackend()
    register_backend(backend, replace=True)
    assert get_backend("fake") is backend


def test_register_backend_builtin_name_raises() -> None:
    class MatplotlibLookalike(FakeBackend):
        name = "matplotlib"

    with pytest.raises(
        BackendRegistrationError, match="already registered under the name 'matplotlib'"
    ):
        register_backend(MatplotlibLookalike())


def test_register_backend_builtin_name_with_replace() -> None:
    class MatplotlibLookalike(FakeBackend):
        name = "matplotlib"

    backend = MatplotlibLookalike()
    register_backend(backend, replace=True)
    assert get_backend("matplotlib") is backend


def test_register_backend_replace_is_keyword_only() -> None:
    with pytest.raises(TypeError, match="positional"):
        cast("Any", register_backend)(FakeBackend(), True)


##################################
#     Tests for get_backend     #
##################################


def test_get_backend_missing() -> None:
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[]),
        pytest.raises(BackendNotFoundError, match="No backend registered under the name 'missing'"),
    ):
        get_backend("missing")


def test_get_backend_missing_lists_known_backends() -> None:
    register_backend(FakeBackend())
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[]),
        pytest.raises(
            BackendNotFoundError,
            match=r"Known backends: \['altair', 'bokeh', 'fake', 'matplotlib', 'plotly', 'xy'\]",
        ),
    ):
        get_backend("missing")


@pytest.mark.parametrize("name", BUILTIN_BACKENDS)
def test_get_backend_builtin(name: str) -> None:
    _REGISTRY.pop(name, None)
    assert get_backend(name).name == name


@matplotlib_available
def test_get_backend_builtin_is_created_once() -> None:
    _REGISTRY.pop("matplotlib", None)
    assert get_backend("matplotlib") is get_backend("matplotlib")


@matplotlib_available
def test_get_backend_builtin_is_cached_in_the_registry() -> None:
    _REGISTRY.pop("matplotlib", None)
    backend = get_backend("matplotlib")
    assert _REGISTRY["matplotlib"] is backend


def test_get_backend_builtin_imports_only_its_module() -> None:
    _REGISTRY.pop("matplotlib", None)
    fake = Mock()
    with patch("plotmux.backends.registry.importlib.import_module", return_value=fake) as mock:
        backend = get_backend("matplotlib")
    mock.assert_called_once_with("plotmux.backends.matplotlib.backend")
    assert backend is fake.MatplotlibBackend.return_value


def test_get_backend_builtin_missing_library_raises_with_the_extra() -> None:
    _REGISTRY.pop("matplotlib", None)
    with (
        patch(
            "plotmux.backends.registry.importlib.import_module",
            side_effect=ImportError("No module named 'matplotlib'"),
        ),
        pytest.raises(
            BackendNotFoundError,
            match=r'Install it with: pip install "plotmux\[matplotlib\]"',
        ),
    ):
        get_backend("matplotlib")


def test_get_backend_builtin_missing_library_keeps_the_cause() -> None:
    _REGISTRY.pop("xy", None)
    error = ImportError("No module named 'xy'")
    with (
        patch("plotmux.backends.registry.importlib.import_module", side_effect=error),
        pytest.raises(BackendNotFoundError) as exc_info,
    ):
        get_backend("xy")
    assert exc_info.value.__cause__ is error


def test_get_backend_registered_wins_over_builtin() -> None:
    class MatplotlibLookalike(FakeBackend):
        name = "matplotlib"

    backend = MatplotlibLookalike()
    register_backend(backend, replace=True)
    with patch("plotmux.backends.registry.importlib.import_module") as mock:
        assert get_backend("matplotlib") is backend
    mock.assert_not_called()


def test_get_backend_entry_point() -> None:
    entry_point = make_entry_point(PluginBackend)
    with patch("plotmux.backends.registry.entry_points", return_value=[entry_point]) as mock:
        backend = get_backend("plugin")
    mock.assert_called_once_with(group=ENTRY_POINT_GROUP, name="plugin")
    assert isinstance(backend, PluginBackend)


def test_get_backend_entry_point_is_created_once() -> None:
    entry_point = make_entry_point(PluginBackend)
    with patch("plotmux.backends.registry.entry_points", return_value=[entry_point]):
        first = get_backend("plugin")
        second = get_backend("plugin")
    assert first is second
    entry_point.load.assert_called_once_with()


def test_get_backend_builtin_wins_over_entry_point() -> None:
    _REGISTRY.pop("matplotlib", None)
    entry_point = make_entry_point(PluginBackend, name="matplotlib")
    fake = Mock()
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        patch("plotmux.backends.registry.importlib.import_module", return_value=fake),
    ):
        get_backend("matplotlib")
    entry_point.load.assert_not_called()


def test_get_backend_entry_point_import_error_raises() -> None:
    entry_point = make_entry_point(None)
    entry_point.load.side_effect = ImportError("No module named 'my_library'")
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(BackendNotFoundError, match=r"'plugin' backend plugin .* cannot be imported"),
    ):
        get_backend("plugin")


def test_get_backend_entry_point_import_error_keeps_the_cause() -> None:
    entry_point = make_entry_point(None)
    error = ImportError("No module named 'my_library'")
    entry_point.load.side_effect = error
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(BackendNotFoundError) as exc_info,
    ):
        get_backend("plugin")
    assert exc_info.value.__cause__ is error


def test_get_backend_entry_point_other_error_propagates() -> None:
    entry_point = make_entry_point(None)
    entry_point.load.side_effect = AttributeError("boom")
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(AttributeError, match="boom"),
    ):
        get_backend("plugin")


def test_get_backend_entry_point_module_instead_of_class_raises() -> None:
    entry_point = make_entry_point(Mock(name="module"))
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(BackendNotFoundError, match="must point to a Backend subclass"),
    ):
        get_backend("plugin")


def test_get_backend_entry_point_not_a_backend_subclass_raises() -> None:
    entry_point = make_entry_point(dict)
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(BackendNotFoundError, match="must point to a Backend subclass"),
    ):
        get_backend("plugin")


def test_get_backend_entry_point_error_is_not_cached() -> None:
    entry_point = make_entry_point(dict)
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[entry_point]),
        pytest.raises(BackendNotFoundError),
    ):
        get_backend("plugin")
    assert "plugin" not in _REGISTRY


#########################################
#     Tests for available_backends     #
#########################################


def test_available_backends_includes_builtin_with_the_library() -> None:
    _REGISTRY.clear()
    availability = dict.fromkeys(_BUILTIN_AVAILABILITY, lambda: False) | {"xy": lambda: True}
    with (
        patch.dict(_BUILTIN_AVAILABILITY, availability),
        patch("plotmux.backends.registry.entry_points", return_value=[]),
    ):
        names = available_backends()
    assert "xy" in names
    assert "matplotlib" not in names


def test_available_backends_excludes_builtin_without_the_library() -> None:
    _REGISTRY.clear()
    availability = dict.fromkeys(_BUILTIN_AVAILABILITY, lambda: False)
    with (
        patch.dict(_BUILTIN_AVAILABILITY, availability),
        patch("plotmux.backends.registry.entry_points", return_value=[]),
    ):
        names = available_backends()
    assert names == frozenset()


def test_available_backends_includes_registered() -> None:
    register_backend(FakeBackend())
    with patch("plotmux.backends.registry.entry_points", return_value=[]):
        assert "fake" in available_backends()


def test_available_backends_includes_entry_point() -> None:
    with patch(
        "plotmux.backends.registry.entry_points", return_value=[make_entry_point(PluginBackend)]
    ):
        assert "plugin" in available_backends()


def test_available_backends_does_not_import_anything() -> None:
    _REGISTRY.clear()
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[]),
        patch("plotmux.backends.registry.importlib.import_module") as mock,
    ):
        available_backends()
    mock.assert_not_called()
    assert _REGISTRY == {}


def test_available_backends_returns_frozenset() -> None:
    with patch("plotmux.backends.registry.entry_points", return_value=[]):
        assert isinstance(available_backends(), frozenset)


@matplotlib_available
def test_available_backends_real_builtin() -> None:
    assert "matplotlib" in available_backends()


####################################
#     Tests for capabilities     #
####################################


def test_capabilities_delegates_to_backend() -> None:
    class RenderersBackend(Backend):
        name = "renderers"
        _RENDERERS: ClassVar[Any] = {int: str}

        def save(self, native: Any, path: Path, fmt: str) -> None:
            del native, path, fmt

    register_backend(RenderersBackend())
    caps = capabilities("renderers")
    assert caps.backend_name == "renderers"
    assert caps.spec_types == frozenset({int})


def test_capabilities_missing_backend() -> None:
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[]),
        pytest.raises(RuntimeError, match="No backend registered"),
    ):
        capabilities("does-not-exist")


########################################
#     Tests for known_backend_names     #
########################################


def test_known_backend_names_includes_builtins() -> None:
    with patch("plotmux.backends.registry.entry_points", return_value=[]):
        names = known_backend_names()
    assert frozenset(_BUILTIN_BACKENDS) <= names


def test_known_backend_names_includes_registered() -> None:
    register_backend(FakeBackend())
    with patch("plotmux.backends.registry.entry_points", return_value=[]):
        names = known_backend_names()
    assert "fake" in names


def test_known_backend_names_includes_entry_point_advertised() -> None:
    entry_point = Mock()
    entry_point.name = "plugin_backend"
    with patch("plotmux.backends.registry.entry_points", return_value=[entry_point]):
        names = known_backend_names()
    assert "plugin_backend" in names


def test_known_backend_names_queries_own_group() -> None:
    with patch("plotmux.backends.registry.entry_points", return_value=[]) as mock:
        known_backend_names()
    mock.assert_called_once_with(group=ENTRY_POINT_GROUP)


def test_known_backend_names_does_not_import_or_register_anything() -> None:
    _REGISTRY.clear()
    with (
        patch("plotmux.backends.registry.entry_points", return_value=[]),
        patch("plotmux.backends.registry.importlib.import_module") as mock_import,
    ):
        names = known_backend_names()
    mock_import.assert_not_called()
    assert "fake" not in names
    assert _REGISTRY == {}


def test_known_backend_names_does_not_load_an_entry_point() -> None:
    entry_point = make_entry_point(PluginBackend)
    with patch("plotmux.backends.registry.entry_points", return_value=[entry_point]):
        known_backend_names()
    entry_point.load.assert_not_called()


def test_known_backend_names_returns_frozenset() -> None:
    with patch("plotmux.backends.registry.entry_points", return_value=[]):
        assert isinstance(known_backend_names(), frozenset)
