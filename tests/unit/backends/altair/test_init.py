from __future__ import annotations

import importlib
from unittest.mock import patch

import plotmux.backends.altair as altair_init
from plotmux.backends.registry import _REGISTRY
from plotmux.testing.fixtures import altair_available

#########################################################
#     Tests for the altair backend __init__     #
#########################################################


@altair_available
def test_altair_backend_registered_when_available() -> None:
    snapshot = dict(_REGISTRY)
    try:
        with patch("plotmux.utils.imports.is_altair_available", lambda: True):
            importlib.reload(altair_init)
        assert "altair" in _REGISTRY
        assert altair_init.__all__ == ["AltairBackend"]
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(altair_init)


def test_altair_backend_not_registered_when_unavailable() -> None:
    snapshot = dict(_REGISTRY)
    try:
        _REGISTRY.pop("altair", None)
        with patch(
            "plotmux.utils.imports.is_altair_available",
            lambda: False,
        ):
            importlib.reload(altair_init)
        assert "altair" not in _REGISTRY
        assert altair_init.__all__ == []
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(snapshot)
        importlib.reload(altair_init)
