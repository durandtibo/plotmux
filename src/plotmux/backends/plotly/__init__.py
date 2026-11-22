r"""Contain the plotly rendering backend.

The backend is registered lazily by ``plotmux.backends.registry``: this
package imports nothing, so it is safe to import even if plotly is not
installed. ``plotmux.backends.plotly.backend`` imports plotly.
"""

from __future__ import annotations

__all__: list[str] = []
