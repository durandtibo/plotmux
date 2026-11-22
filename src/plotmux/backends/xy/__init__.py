r"""Contain the xy rendering backend.

The backend is registered lazily by ``plotmux.backends.registry``: this
package imports nothing, so it is safe to import even if xy is not
installed. ``plotmux.backends.xy.backend`` imports xy.
"""

from __future__ import annotations

__all__: list[str] = []
