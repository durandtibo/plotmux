from __future__ import annotations

__all__ = []

import webbrowser

import pytest


@pytest.fixture(autouse=True)
def _no_browser() -> None:
    r"""Register a browser that runs ``true`` instead of opening a window, so
    ``Figure.show`` can run for real without a display."""
    webbrowser.register("plotmux-test", None, webbrowser.GenericBrowser("true"), preferred=True)
