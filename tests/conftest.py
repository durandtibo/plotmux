from __future__ import annotations

__all__ = []


import pytest

from plotmux.utils.imports import is_matplotlib_available

if is_matplotlib_available():
    from matplotlib import pyplot as plt


@pytest.fixture(autouse=True)
def _close_plt_figure() -> None:
    if is_matplotlib_available():
        plt.close()
