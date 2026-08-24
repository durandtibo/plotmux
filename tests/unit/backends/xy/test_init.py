from __future__ import annotations

import importlib
from unittest.mock import patch

import plotmux.backends.xy as xy_init
from plotmux.backends.registry import _REGISTRY


def test_xy_backend_not_registered_when_unavailable() -> None:
    snapshot = dict(_REGISTRY)
    try:
        _REGISTRY.pop("xy", None)
        with patch(
            "plotmux.utils.imports.is_xy_available",
            lambda: False,
        ):
            importlib.reload(xy_init)
        assert "xy" not in _REGISTRY
        assert xy_init.__all__ == []
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(xy_init)
