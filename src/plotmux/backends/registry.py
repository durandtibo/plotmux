r"""Contain the registry of available rendering backends."""

from __future__ import annotations

__all__ = ["get_backend", "register_backend"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotmux.backends.base import Backend

_REGISTRY: dict[str, Backend] = {}


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
