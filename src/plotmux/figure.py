r"""Contain the ``Figure`` wrapper returned by the public API."""

from __future__ import annotations

__all__ = ["Figure"]

import io
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from plotmux.backends.registry import get_backend
from plotmux.export import save

if TYPE_CHECKING:
    from pathlib import Path

    from plotmux.specs import BaseSpec

# The set of IPython/Jupyter rich-display dunder methods ``Figure`` forwards
# to the native object (see ``__getattr__``). This is not an exhaustive list
# of every ``_repr_*_`` IPython recognizes, only the ones a plotting
# library's native figure realistically defines: bokeh's ``figure`` defines
# ``_repr_html_``, and altair's ``Chart`` defines ``_repr_mimebundle_`` (see
# each backend's own native object). ``_repr_png_`` is deliberately not in
# this set: it gets its own method below, with a matplotlib-specific
# fallback (see ``_repr_png_``). Keeping this list explicit and closed --
# rather than forwarding arbitrary attribute access -- means ``Figure``
# only ever grows new display behavior on purpose, never as a side effect
# of some unrelated attribute happening to exist on ``native``.
_REPR_METHODS = frozenset({"_repr_html_", "_repr_mimebundle_", "_repr_svg_", "_repr_jpeg_"})


@dataclass
class Figure:
    r"""Wrap the result of rendering a spec through a backend.

    ``Figure`` is the object returned to the user by the public API
    (``plotmux.hist``, ``plotmux.line``, ``plotmux.scatter``, ...).
    It keeps the spec that produced it, the name of the backend that
    rendered it, and the backend's native figure object.

    Args:
        spec: The spec that was rendered.
        backend_name: The name of the backend that rendered
            ``native``.
        native: The backend's native figure object (e.g. a
            matplotlib ``Figure``).
    """

    spec: BaseSpec
    backend_name: str
    native: Any

    def show(self) -> None:
        r"""Display the figure using the backend's default viewer.

        Raises:
            NotImplementedError: if the backend's native figure
                object does not expose a ``show`` method.
        """
        show = getattr(self.native, "show", None)
        if show is None:
            msg = f"The native object of type {type(self.native)} does not support 'show'"
            raise NotImplementedError(msg)
        show()

    @property
    def supported_formats(self) -> frozenset[str]:
        r"""The export formats accepted by ``save`` for this figure's
        backend.

        Different backends support different export formats (e.g. the
        ``bokeh`` backend only supports ``"html"``, since static image
        export requires an extra, environment-specific dependency).
        This lets callers check what is supported ahead of time
        instead of discovering it via a ``ValueError`` from ``save``.

        Returns:
            The set of export formats accepted by ``save``.
        """
        return get_backend(self.backend_name).supported_formats

    def save(self, path: str | Path) -> None:
        r"""Save the figure to a file.

        The export format is inferred from the file suffix (e.g.
        ``.png``, ``.svg``).

        Args:
            path: The path where to save the figure.

        Raises:
            ValueError: if ``path`` has no suffix, so the export
                format cannot be inferred.
        """
        save(self, path)

    def _repr_png_(self) -> bytes | None:
        r"""Render the figure to PNG bytes for Jupyter's rich display.

        Tries ``native``'s own ``_repr_png_`` first, like every other
        method in ``_REPR_METHODS`` (see ``__getattr__``). matplotlib's
        ``Figure`` defines no such method itself -- outside
        ``%matplotlib inline``, IPython displays it through a
        formatter registered on the ``Figure`` *class*, not through
        an instance method plotmux could simply forward to. So this
        falls back to a duck-typed ``native.canvas.print_png``:
        ``MatplotlibBackend`` attaches a working ``_repr_png_`` to
        every ``Figure`` it builds (see
        ``plotmux.backends.matplotlib.backend``), which this picks up
        via the first branch above; this second branch is a plain
        structural fallback for any other native object shaped the
        same way, without plotmux importing matplotlib itself here --
        that would break the "a backend module is only imported when
        its library is installed" rule every other backend follows.

        Returns:
            The PNG-encoded bytes, or ``None`` if neither ``native``
                nor its ``canvas`` can produce one.
        """
        method = getattr(self.native, "_repr_png_", None)
        if method is not None:
            return method()
        print_png = getattr(getattr(self.native, "canvas", None), "print_png", None)
        if print_png is None:
            return None
        buffer = io.BytesIO()
        print_png(buffer)
        return buffer.getvalue()

    def __getattr__(self, name: str) -> Any:
        r"""Forward IPython/Jupyter rich-display lookups to ``native``.

        This is what makes a ``Figure`` display itself automatically
        as the last expression of a Jupyter cell, exactly as its
        ``native`` object would on its own -- without every backend
        having to reimplement its own ``_repr_html_``/... wrapper,
        and without ``Figure`` hardcoding which of those methods a
        given backend's native object happens to define.

        Only called by Python when normal attribute lookup on
        ``Figure`` itself fails, so it never shadows a real
        ``Figure`` attribute or method. Restricted to the fixed
        ``_REPR_METHODS`` set (rather than forwarding any missing
        attribute) so a typo in user code (e.g. ``fig.sav(...)``)
        still raises a clear ``AttributeError`` instead of silently
        forwarding to ``native`` and failing there with a confusing
        error.

        Args:
            name: The attribute name that was looked up.

        Returns:
            The bound method of the same name on ``native``.

        Raises:
            AttributeError: if ``name`` is not a known rich-display
                method, or ``native`` does not define it.
        """
        if name in _REPR_METHODS:
            method = getattr(self.native, name, None)
            if method is not None:
                return method
        msg = f"{type(self).__name__!r} object has no attribute {name!r}"
        raise AttributeError(msg)

    def to_native(self) -> Any:
        r"""Return the backend's native figure object.

        This is the escape hatch to reach backend-specific
        functionality that is not exposed by the unified API.

        Returns:
            The backend's native figure object.
        """
        return self.native
