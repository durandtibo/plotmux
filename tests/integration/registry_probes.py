r"""Probes run in a new Python process by ``test_registry.py``.

Each probe is a function run by ``multiprocessing`` with the ``spawn``
start method, so ``plotmux`` and the plotting libraries are imported for
the first time by the probe and ``sys.modules`` is not shared with the
test session. The modules are imported with ``importlib`` inside the
probes because the import is the behaviour under test.
"""

from __future__ import annotations

__all__ = []

import sys
from importlib import import_module
from typing import Any, cast

LIBRARIES = ("altair", "bokeh", "matplotlib", "plotly", "xy")


def _loaded_libraries() -> list[str]:
    return [name for name in LIBRARIES if name in sys.modules]


def backend_modules_after_import() -> list[str]:
    import_module("plotmux")
    return sorted(
        name
        for name in sys.modules
        if name.startswith("plotmux.backends.") and name.split(".")[2] in LIBRARIES
    )


def libraries_after_import() -> list[str]:
    import_module("plotmux")
    return _loaded_libraries()


def libraries_after_get_backend(name: str) -> list[str]:
    import_module("plotmux.backends").get_backend(name)
    return _loaded_libraries()


def plugin_loaded_after_import(path: str) -> bool:
    sys.path.insert(0, path)
    import_module("plotmux")
    return "plotmux_plugin" in sys.modules


def plugin_loaded_after_set_backend(path: str) -> bool:
    sys.path.insert(0, path)
    import_module("plotmux").set_backend("plugin")
    return "plotmux_plugin" in sys.modules


def plugin_loaded_on_first_use(path: str) -> tuple[bool, bool, str]:
    sys.path.insert(0, path)
    backends = import_module("plotmux.backends")
    before = "plotmux_plugin" in sys.modules
    backend = backends.get_backend("plugin")
    return before, "plotmux_plugin" in sys.modules, type(backend).__name__


def plugin_is_available(path: str) -> bool:
    sys.path.insert(0, path)
    return "plugin" in import_module("plotmux.backends").available_backends()


def plugin_render(path: str) -> tuple[str, str]:
    sys.path.insert(0, path)
    figure = import_module("plotmux").hist([1, 2, 3], backend="plugin")
    return figure.backend_name, figure.native


def register_plugin_with_a_builtin_name(path: str, *, replace: bool) -> str:
    sys.path.insert(0, path)
    plugin = import_module("plotmux_plugin")
    backends = import_module("plotmux.backends")
    exceptions = import_module("plotmux.exceptions")
    try:
        backends.register_backend(plugin.PluginBackend(), replace=replace)
    except exceptions.BackendRegistrationError:
        return "refused"
    return type(backends.get_backend("matplotlib")).__name__


def missing_library_message(name: str) -> str:
    # A ``None`` entry makes ``import <name>`` raise ``ImportError``.
    cast("Any", sys.modules)[name] = None
    backends = import_module("plotmux.backends")
    exceptions = import_module("plotmux.exceptions")
    try:
        backends.get_backend(name)
    except exceptions.BackendNotFoundError as err:
        return str(err)
    return ""


def render_with_a_missing_library() -> str:
    cast("Any", sys.modules)["matplotlib"] = None
    return import_module("plotmux").hist([1, 2, 3], backend="xy").backend_name
