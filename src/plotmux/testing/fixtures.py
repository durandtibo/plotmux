r"""Define some pytest fixtures for testing.

`pytest` is required to use these fixtures.
"""

from __future__ import annotations

__all__ = [
    "matplotlib_available",
    "matplotlib_not_available",
]

import pytest

from plotmux.utils.imports import is_matplotlib_available

matplotlib_available: pytest.MarkDecorator = pytest.mark.skipif(
    not is_matplotlib_available(), reason="Requires matplotlib"
)
matplotlib_not_available: pytest.MarkDecorator = pytest.mark.skipif(
    is_matplotlib_available(), reason="Skip if matplotlib is available"
)
