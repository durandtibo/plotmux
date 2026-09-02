r"""Contain the plotly rendering backend.

Importing this module registers the plotly backend if and only if plotly
is installed. It is safe to import even if plotly is not installed: the
module simply does not register the backend in that case.
"""

from __future__ import annotations

__all__: list[str] = []

from plotmux.utils.imports import is_plotly_available

if is_plotly_available():
    from plotmux.backends.plotly.backend import PlotlyBackend
    from plotmux.backends.registry import register_backend

    register_backend(PlotlyBackend())
    __all__ += ["PlotlyBackend"]
