from __future__ import annotations

import importlib
from unittest.mock import patch

import plotmux.backends.bokeh as bokeh_init
from plotmux.backends.registry import _REGISTRY
from plotmux.testing.fixtures import bokeh_available

#######################################################
#     Tests for the bokeh backend __init__     #
#######################################################


@bokeh_available
def test_bokeh_backend_registered_when_available() -> None:
    snapshot = dict(_REGISTRY)
    try:
        with patch("plotmux.utils.imports.is_bokeh_available", lambda: True):
            importlib.reload(bokeh_init)
        assert "bokeh" in _REGISTRY
        assert bokeh_init.__all__ == ["BokehBackend"]
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(bokeh_init)


def test_bokeh_backend_not_registered_when_unavailable() -> None:
    snapshot = dict(_REGISTRY)
    try:
        _REGISTRY.pop("bokeh", None)
        with patch(
            "plotmux.utils.imports.is_bokeh_available",
            lambda: False,
        ):
            importlib.reload(bokeh_init)
        assert "bokeh" not in _REGISTRY
        assert bokeh_init.__all__ == []
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(bokeh_init)
