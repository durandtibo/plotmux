r"""Contain the registry of available rendering backends.

A backend is found by name, in this order: an instance registered with
``register_backend``, a built-in backend (``_BUILTIN_BACKENDS``), then a
third-party backend advertised in the ``plotmux.backends`` entry-point
group. A backend is imported and instantiated on its first use only, so
``import plotmux`` imports no backend, no plotting library and no plugin.
"""

from __future__ import annotations

__all__ = [
    "ENTRY_POINT_GROUP",
    "available_backends",
    "capabilities",
    "get_backend",
    "known_backend_names",
    "register_backend",
]

import importlib
from importlib.metadata import entry_points
from typing import TYPE_CHECKING

from plotmux.backends.base import Backend
from plotmux.exceptions import BackendNotFoundError, BackendRegistrationError
from plotmux.utils.imports import (
    is_altair_available,
    is_bokeh_available,
    is_matplotlib_available,
    is_plotly_available,
    is_xy_available,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotmux.backends.base import BackendCapabilities

# The instances that can be used: registered with ``register_backend``, or
# created on the first use of a built-in or an entry-point backend.
_REGISTRY: dict[str, Backend] = {}

# The entry-point group third-party packages use to plug in a backend
# without editing plotmux's source. An entry point is named after the
# backend and its value is ``package.module:BackendClass``.
ENTRY_POINT_GROUP = "plotmux.backends"

# Maps the name of a built-in backend to ``module:Class``. The module is
# imported on the first use of the name, never at ``import plotmux``.
_BUILTIN_BACKENDS = {
    "altair": "plotmux.backends.altair.backend:AltairBackend",
    "bokeh": "plotmux.backends.bokeh.backend:BokehBackend",
    "matplotlib": "plotmux.backends.matplotlib.backend:MatplotlibBackend",
    "plotly": "plotmux.backends.plotly.backend:PlotlyBackend",
    "xy": "plotmux.backends.xy.backend:XyBackend",
}

# Tells if the plotting library of a built-in backend can be imported.
_BUILTIN_AVAILABILITY: dict[str, Callable[[], bool]] = {
    "altair": is_altair_available,
    "bokeh": is_bokeh_available,
    "matplotlib": is_matplotlib_available,
    "plotly": is_plotly_available,
    "xy": is_xy_available,
}


def register_backend(backend: Backend, *, replace: bool = False) -> None:
    r"""Register a backend instance under its ``name``.

    A name already used by a registered backend or by a built-in
    backend is refused unless ``replace=True``, so installing a package
    can never take over a built-in name by accident.

    Args:
        backend: The backend instance to register.
        replace: If ``True``, replace the backend already registered
            under the same name, or the built-in backend of that name.

    Raises:
        BackendRegistrationError: if the name is already used by a
            registered or a built-in backend and ``replace`` is
            ``False``. Also a ``ValueError``.

    Example:
        ```pycon
        >>> from plotmux.backends.registry import register_backend, get_backend
        >>> class MyBackend:
        ...     name = "my_backend"
        ...
        >>> register_backend(MyBackend())
        >>> get_backend("my_backend")  # doctest: +ELLIPSIS
        <....MyBackend object at 0x...>
        >>> register_backend(MyBackend(), replace=True)

        ```
    """
    name = backend.name
    if not replace and (name in _REGISTRY or name in _BUILTIN_BACKENDS):
        msg = (
            f"A backend is already registered under the name {name!r}. "
            f"Use register_backend(..., replace=True) to replace it."
        )
        raise BackendRegistrationError(msg)
    _REGISTRY[name] = backend


def get_backend(name: str) -> Backend:
    r"""Get a backend by name.

    The backend is looked up in the registered instances, then in the
    built-in backends, then in the entry-point group
    ``plotmux.backends``. A built-in or entry-point backend is
    imported and instantiated on the first request for its name, and
    the instance is reused afterwards. Only the module of that name is
    imported.

    Args:
        name: The name of the backend to retrieve.

    Returns:
        The backend instance.

    Raises:
        BackendNotFoundError: if no backend has this name, or if its
            module cannot be imported (typically because its plotting
            library is not installed; the message gives the extra to
            install). Also a ``RuntimeError``.
    """
    backend = _REGISTRY.get(name)
    if backend is None:
        backend = _load_builtin(name) if name in _BUILTIN_BACKENDS else _load_entry_point(name)
        # Keep the first instance if another thread created one meanwhile.
        backend = _REGISTRY.setdefault(name, backend)
    return backend


def available_backends() -> frozenset[str]:
    r"""Return the names of the backends that can be used.

    These are the registered backends, the built-in backends whose
    plotting library is installed, and the names advertised by an
    installed plugin (a plugin is imported on its first use, so its
    library is not checked here). Nothing is imported.

    Returns:
        The set of usable backend names.

    Example:
        ```pycon
        >>> from plotmux.backends.registry import available_backends
        >>> "matplotlib" in available_backends()
        True

        ```
    """
    builtin = {name for name, is_available in _BUILTIN_AVAILABILITY.items() if is_available()}
    return frozenset(builtin) | _entry_point_names() | frozenset(_REGISTRY)


def capabilities(name: str) -> BackendCapabilities:
    r"""Get a registered backend's capabilities by name.

    A thin convenience wrapper around ``get_backend(name).capabilities()``
    for a caller that wants to check spec-type/caveat support without
    otherwise needing the backend instance itself.

    Args:
        name: The name of the backend to query.

    Returns:
        The backend's ``BackendCapabilities``.

    Raises:
        BackendNotFoundError: if no backend has this name (see
            ``get_backend``).
    """
    return get_backend(name).capabilities()


def known_backend_names() -> frozenset[str]:
    r"""Return every backend name that could resolve, without importing
    or registering anything.

    This is the union of the built-in backend names, the names
    advertised under the ``plotmux.backends`` entry-point group
    (reading the metadata of the installed packages does not import
    them), and the registered names. Used by
    ``plotmux.config.set_backend`` to reject a typo'd name immediately,
    at zero import cost. A name in this set may still fail at render
    time if its plotting library is not installed (see
    ``available_backends``).

    Returns:
        The set of currently-resolvable backend names.
    """
    return frozenset(_BUILTIN_BACKENDS) | _entry_point_names() | frozenset(_REGISTRY)


def _entry_point_names() -> frozenset[str]:
    r"""Return the backend names advertised in the entry-point group.

    Only the installed metadata is read: no plugin is imported.

    Returns:
        The names of the entry points of the group.
    """
    return frozenset(ep.name for ep in entry_points(group=ENTRY_POINT_GROUP))


def _load_builtin(name: str) -> Backend:
    r"""Import the module of a built-in backend and instantiate it.

    Args:
        name: The name of a built-in backend.

    Returns:
        A new backend instance.

    Raises:
        BackendNotFoundError: if the module cannot be imported.
    """
    module_name, _, class_name = _BUILTIN_BACKENDS[name].partition(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as err:
        msg = (
            f"The {name!r} backend cannot be used because its plotting library "
            f"cannot be imported ({err}). "
            f'Install it with: pip install "plotmux[{name}]"'
        )
        raise BackendNotFoundError(msg) from err
    return getattr(module, class_name)()


def _load_entry_point(name: str) -> Backend:
    r"""Load the entry-point backend of this name and instantiate it.

    The value of the entry point is ``package.module:BackendClass``.

    Args:
        name: The name of a backend advertised in the entry-point
            group.

    Returns:
        A new backend instance.

    Raises:
        BackendNotFoundError: if no entry point has this name, its
            module cannot be imported, or it does not point to a
            ``Backend`` subclass.
    """
    matches = entry_points(group=ENTRY_POINT_GROUP, name=name)
    if not matches:
        msg = (
            f"No backend registered under the name {name!r}. "
            f"Known backends: {sorted(known_backend_names())}"
        )
        raise BackendNotFoundError(msg)
    entry_point = next(iter(matches))
    try:
        backend_class = entry_point.load()
    except ImportError as err:
        msg = (
            f"The {name!r} backend plugin ({entry_point.value}) cannot be imported "
            f"({err}). Is its plotting library installed?"
        )
        raise BackendNotFoundError(msg) from err
    if not (isinstance(backend_class, type) and issubclass(backend_class, Backend)):
        msg = (
            f"The entry point {name!r} ({entry_point.value}) must point to a Backend "
            f"subclass with the value 'package.module:BackendClass', but received "
            f"{backend_class!r}"
        )
        raise BackendNotFoundError(msg)
    return backend_class()
