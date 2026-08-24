r"""Contain the bokeh rendering backend.

Importing this module registers the bokeh backend if and only if bokeh
is installed. It is safe to import even if bokeh is not installed: the
module simply does not register the backend in that case.
"""

from __future__ import annotations

__all__: list[str] = []

from plotmux.utils.imports import is_bokeh_available

if is_bokeh_available():
    from plotmux.backends.bokeh.backend import BokehBackend
    from plotmux.backends.registry import register_backend

    register_backend(BokehBackend())
    __all__ += ["BokehBackend"]
