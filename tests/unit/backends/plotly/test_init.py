from __future__ import annotations

import importlib
from unittest.mock import patch

import plotmux.backends.plotly as plotly_init
from plotmux.backends.registry import _REGISTRY
from plotmux.testing.fixtures import plotly_available

#########################################################
#     Tests for the plotly backend __init__     #
#########################################################


@plotly_available
def test_plotly_backend_registered_when_available() -> None:
    snapshot = dict(_REGISTRY)
    try:
        with patch("plotmux.utils.imports.is_plotly_available", lambda: True):
            importlib.reload(plotly_init)
        assert "plotly" in _REGISTRY
        assert plotly_init.__all__ == ["PlotlyBackend"]
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(plotly_init)


def test_plotly_backend_not_registered_when_unavailable() -> None:
    snapshot = dict(_REGISTRY)
    try:
        _REGISTRY.pop("plotly", None)
        with patch(
            "plotmux.utils.imports.is_plotly_available",
            lambda: False,
        ):
            importlib.reload(plotly_init)
        assert "plotly" not in _REGISTRY
        assert plotly_init.__all__ == []
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(plotly_init)
