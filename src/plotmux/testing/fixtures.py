r"""Define some pytest fixtures for testing.

`pytest` is required to use these fixtures.
"""

from __future__ import annotations

__all__ = [
    "bokeh_available",
    "bokeh_not_available",
    "matplotlib_available",
    "matplotlib_not_available",
    "xy_available",
    "xy_not_available",
]

import pytest

from plotmux.utils.imports import is_bokeh_available, is_matplotlib_available, is_xy_available

bokeh_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_bokeh_available(), reason="Requires bokeh"
)
bokeh_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_bokeh_available(), reason="Skip if bokeh is available"
)

matplotlib_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_matplotlib_available(), reason="Requires matplotlib"
)
matplotlib_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_matplotlib_available(), reason="Skip if matplotlib is available"
)

xy_available: pytest.MarkDecorator = pytest.mark.skipif(not is_xy_available(), reason="Requires xy")
xy_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_xy_available(), reason="Skip if xy is available"
)
