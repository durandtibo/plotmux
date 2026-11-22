r"""Contain the bokeh rendering backend.

The backend is registered lazily by ``plotmux.backends.registry``: this
package imports nothing, so it is safe to import even if bokeh is not
installed. ``plotmux.backends.bokeh.backend`` imports bokeh.
"""

from __future__ import annotations

__all__: list[str] = []
