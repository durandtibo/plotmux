from __future__ import annotations

__all__ = []

import os

import pytest

from plotmux.utils.imports import is_matplotlib_available

# A non-interactive matplotlib backend: ``Figure.show`` must never open a
# window (or block) during the tests.
os.environ.setdefault("MPLBACKEND", "Agg")

if is_matplotlib_available():
    from matplotlib import pyplot as plt


@pytest.fixture(autouse=True)
def _close_plt_figure() -> None:
    if is_matplotlib_available():
        plt.close()
