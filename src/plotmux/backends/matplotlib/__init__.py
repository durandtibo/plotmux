r"""Contain the matplotlib rendering backend.

The backend is registered lazily by ``plotmux.backends.registry``: this
package imports nothing, so it is safe to import even if matplotlib is not
installed. ``plotmux.backends.matplotlib.backend`` imports matplotlib.
"""

from __future__ import annotations

__all__: list[str] = []
