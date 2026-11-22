r"""Contain the altair rendering backend.

The backend is registered lazily by ``plotmux.backends.registry``: this
package imports nothing, so it is safe to import even if altair is not
installed. ``plotmux.backends.altair.backend`` imports altair.
"""

from __future__ import annotations

__all__: list[str] = []
