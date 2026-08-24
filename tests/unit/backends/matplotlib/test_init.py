from __future__ import annotations

import importlib
from unittest.mock import patch

import plotmux.backends.matplotlib as matplotlib_init
from plotmux.backends.registry import _REGISTRY
from plotmux.testing.fixtures import matplotlib_available

#####################################################
#     Tests for the matplotlib backend __init__     #
#####################################################


@matplotlib_available
def test_matplotlib_backend_registered_when_available() -> None:
    snapshot = dict(_REGISTRY)
    try:
        with patch("plotmux.utils.imports.is_matplotlib_available", lambda: True):
            importlib.reload(matplotlib_init)
        assert "matplotlib" in _REGISTRY
        assert matplotlib_init.__all__ == ["MatplotlibBackend"]
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(matplotlib_init)


def test_matplotlib_backend_not_registered_when_unavailable() -> None:
    snapshot = dict(_REGISTRY)
    try:
        _REGISTRY.pop("matplotlib", None)
        with patch(
            "plotmux.utils.imports.is_matplotlib_available",
            lambda: False,
        ):
            importlib.reload(matplotlib_init)
        assert "matplotlib" not in _REGISTRY
        assert matplotlib_init.__all__ == []
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(matplotlib_init)
