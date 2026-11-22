r"""End-to-end registry coverage, in a new Python process each time (see
``registry_probes``): the lazy import of the backends, the discovery of a
plugin through the installed metadata (a real distribution on ``sys.path``),
and the missing libraries."""

from __future__ import annotations

import multiprocessing
from typing import TYPE_CHECKING, Any

import pytest

from plotmux.testing.fixtures import matplotlib_available, xy_available
from tests.integration import registry_probes

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

PLUGIN_MODULE = """
from plotmux.backends.base import Backend, BackendCapabilities


class PluginBackend(Backend):
    name = "plugin"

    def capabilities(self):
        return BackendCapabilities(
            name="plugin",
            formats=frozenset({"txt"}),
            grid_formats=frozenset({"txt"}),
            legend_locations=frozenset(),
            markers=frozenset(),
        )

    def draw(self, scene):
        return "rendered"

    def save(self, native, path, fmt):
        path.write_text(native)
"""


def run(probe: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    r"""Run a probe in a new Python process and return its result."""
    context = multiprocessing.get_context("spawn")
    with context.Pool(1) as pool:
        return pool.apply(probe, args, kwargs)


def install_plugin(path: Path, backend_name: str = "plugin") -> str:
    r"""Install a fake distribution that advertises the ``plugin`` entry point."""
    (path / "plotmux_plugin.py").write_text(
        PLUGIN_MODULE.replace('name = "plugin"', f'name = "{backend_name}"')
    )
    dist_info = path / "plotmux_plugin-0.0.1.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: plotmux-plugin\nVersion: 0.0.1\n"
    )
    (dist_info / "entry_points.txt").write_text(
        "[plotmux.backends]\nplugin = plotmux_plugin:PluginBackend\n"
    )
    return str(path)


@pytest.fixture
def plugin_path(tmp_path: Path) -> str:
    return install_plugin(tmp_path)


#######################################
#     Tests for the lazy import     #
#######################################


def test_import_plotmux_imports_no_backend() -> None:
    assert run(registry_probes.backend_modules_after_import) == []


def test_import_plotmux_imports_no_plotting_library() -> None:
    assert run(registry_probes.libraries_after_import) == []


@matplotlib_available
def test_get_backend_imports_only_the_requested_backend() -> None:
    assert run(registry_probes.libraries_after_get_backend, "matplotlib") == ["matplotlib"]


@xy_available
def test_get_backend_xy_does_not_import_matplotlib() -> None:
    assert run(registry_probes.libraries_after_get_backend, "xy") == ["xy"]


def test_import_plotmux_reads_no_entry_point(plugin_path: str) -> None:
    assert run(registry_probes.plugin_loaded_after_import, plugin_path) is False


def test_set_backend_does_not_load_the_plugin(plugin_path: str) -> None:
    assert run(registry_probes.plugin_loaded_after_set_backend, plugin_path) is False


######################################
#     Tests for a plugin backend     #
######################################


def test_plugin_is_loaded_on_first_use(plugin_path: str) -> None:
    assert run(registry_probes.plugin_loaded_on_first_use, plugin_path) == (
        False,
        True,
        "PluginBackend",
    )


def test_plugin_is_listed_as_available(plugin_path: str) -> None:
    assert run(registry_probes.plugin_is_available, plugin_path) is True


def test_plugin_renders_through_the_public_api(plugin_path: str) -> None:
    assert run(registry_probes.plugin_render, plugin_path) == ("plugin", "rendered")


def test_plugin_cannot_take_over_a_builtin_name(tmp_path: Path) -> None:
    path = install_plugin(tmp_path, backend_name="matplotlib")
    assert (
        run(registry_probes.register_plugin_with_a_builtin_name, path, replace=False) == "refused"
    )


def test_replace_true_takes_over_a_builtin_name(tmp_path: Path) -> None:
    path = install_plugin(tmp_path, backend_name="matplotlib")
    assert (
        run(registry_probes.register_plugin_with_a_builtin_name, path, replace=True)
        == "PluginBackend"
    )


####################################
#     Tests for missing libraries     #
####################################


@pytest.mark.parametrize("name", ["altair", "bokeh", "matplotlib", "plotly", "xy"])
def test_missing_library_raises_with_the_extra(name: str) -> None:
    message = run(registry_probes.missing_library_message, name)
    assert f'pip install "plotmux[{name}]"' in message


@xy_available
def test_missing_library_leaves_other_backends_usable() -> None:
    assert run(registry_probes.render_with_a_missing_library) == "xy"
