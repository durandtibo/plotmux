r"""Contain the registry of available rendering backends."""

from __future__ import annotations

__all__ = ["ENTRY_POINT_GROUP", "get_backend", "load_entry_point_backends", "register_backend"]

import warnings
from importlib.metadata import entry_points
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.metadata import EntryPoint

    from plotmux.backends.base import Backend

_REGISTRY: dict[str, Backend] = {}

# The entry-point group third-party packages use to plug in a backend
# without editing plotmux's source. See ``load_entry_point_backends``.
ENTRY_POINT_GROUP = "plotmux.backends"


def register_backend(backend: Backend) -> None:
    r"""Register a backend instance under its ``name``.

    Registering a backend under a name that is already registered
    replaces the previous registration.

    Args:
        backend: The backend instance to register.

    Example:
        ```pycon
        >>> from plotmux.backends.registry import register_backend, get_backend
        >>> class MyBackend:
        ...     name = "my_backend"
        ...
        >>> register_backend(MyBackend())
        >>> get_backend("my_backend")  # doctest: +ELLIPSIS
        <....MyBackend object at 0x...>

        ```
    """
    _REGISTRY[backend.name] = backend


def get_backend(name: str) -> Backend:
    r"""Get a registered backend by name.

    Args:
        name: The name of the backend to retrieve.

    Returns:
        The registered backend instance.

    Raises:
        RuntimeError: if no backend is registered under ``name``.
            This typically means the backend's underlying plotting
            library is not installed.
    """
    try:
        return _REGISTRY[name]
    except KeyError as err:
        available = sorted(_REGISTRY)
        msg = (
            f"No backend registered under the name {name!r}. This backend's "
            f"underlying plotting library may not be installed. "
            f"Available backends: {available}"
        )
        raise RuntimeError(msg) from err


def load_entry_point_backends() -> None:
    r"""Import every backend advertised via the ``plotmux.backends``
    entry-point group.

    plotmux's own ``matplotlib`` and ``xy`` backends are wired in
    directly (see ``plotmux.__init__``); this function is the plug-in
    mechanism for *third-party* backends, so a separate package can
    add a new backend without editing plotmux's source. To do so, a
    package declares an entry point of the form::

        [project.entry-points."plotmux.backends"]
        my_backend = "my_package.plotmux_backend"

    pointing at a module that calls ``register_backend(...)`` at
    import time (the same pattern used by
    ``plotmux.backends.matplotlib``/``plotmux.backends.xy``). Calling
    this function imports every such module, which registers itself
    as a side effect.

    A module that fails to import because its own underlying plotting
    library is not installed (``ImportError``) is silently skipped,
    mirroring how the built-in backends guard their own registration
    behind an ``is_..._available()`` check. Any other exception raised
    while loading a plugin (a bug in the plugin itself, e.g. a broken
    ``register_backend(...)`` call) is caught and turned into a
    warning instead of propagating: a broken third-party plugin must
    never be able to crash ``import plotmux`` for every user, only
    fail to register itself.
    """
    for ep in entry_points(group=ENTRY_POINT_GROUP):
        _load_entry_point(ep)


def _load_entry_point(ep: EntryPoint) -> None:
    try:
        ep.load()
    except ImportError:
        pass
    except Exception as err:  # noqa: BLE001
        msg = (
            f"Skipping plotmux backend plugin {ep.name!r} ({ep.value}): "
            f"it raised {err!r} while loading"
        )
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
