r"""Contain the base class for backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = ["BaseSpec"]

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseSpec:
    r"""Define the base class for chart specifications.

    A spec is a plain, backend-agnostic description of *what* to
    plot (data + encoding + style). It must never import or hold a
    reference to a plotting library object. Turning a spec into a
    native figure is the responsibility of a backend (see
    ``plotmux.backends``).

    Subclasses are expected to be frozen dataclasses and may use
    ``__post_init__`` to validate their fields.
    """
