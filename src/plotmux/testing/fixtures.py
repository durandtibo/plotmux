r"""Define ``pytest`` markers to skip tests based on the availability of
``plotmux``'s optional backend dependencies (``altair``, ``bokeh``,
``matplotlib``, ``plotly``, ``xy``).

``pytest`` is required to use these fixtures. Each ``<package>_available``
marker skips the test unless the package is installed, and each
``<package>_not_available`` marker skips the test if the package is
installed, which is useful to test the "missing dependency" error
paths (see ``plotmux.utils.imports``).

Example:
    ```pycon
    >>> from plotmux.testing.fixtures import matplotlib_available
    >>> @matplotlib_available
    ... def test_something() -> None:
    ...     pass
    ...

    ```
"""

from __future__ import annotations

__all__ = [
    "altair_available",
    "altair_not_available",
    "bokeh_available",
    "bokeh_not_available",
    "matplotlib_available",
    "matplotlib_not_available",
    "plotly_available",
    "plotly_not_available",
    "xy_available",
    "xy_not_available",
]

import pytest

from plotmux.utils.imports import (
    is_altair_available,
    is_bokeh_available,
    is_matplotlib_available,
    is_plotly_available,
    is_xy_available,
)

altair_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_altair_available(), reason="Requires altair"
)
altair_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_altair_available(), reason="Skip if altair is available"
)

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

plotly_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_plotly_available(), reason="Requires plotly"
)
plotly_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_plotly_available(), reason="Skip if plotly is available"
)

xy_available: pytest.MarkDecorator = pytest.mark.skipif(not is_xy_available(), reason="Requires xy")
xy_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_xy_available(), reason="Skip if xy is available"
)
