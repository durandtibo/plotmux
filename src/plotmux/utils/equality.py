r"""Contain the base class of the immutable value objects of the package."""

from __future__ import annotations

__all__ = ["ValueObject"]

from dataclasses import dataclass, fields

from coola.equality import objects_are_equal


@dataclass(frozen=True, eq=False)
class ValueObject:
    r"""Define the base class of the frozen dataclasses that hold
    arrays.

    Two value objects are equal if they have the same type and equal
    fields, where arrays are compared by value (a plain dataclass
    ``==`` raises on an array field). A value object holds arrays, so
    it is not hashable.

    Example:
        ```pycon
        >>> import numpy as np
        >>> from dataclasses import dataclass
        >>> from plotmux.utils.equality import ValueObject
        >>> @dataclass(frozen=True, eq=False)
        ... class Data(ValueObject):
        ...     values: np.ndarray
        ...
        >>> Data(np.arange(3)) == Data(np.arange(3))
        True
        >>> Data(np.arange(3)) == Data(np.arange(4))
        False

        ```
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject) or type(self) is not type(other):
            return NotImplemented
        return objects_are_equal(
            {f.name: getattr(self, f.name) for f in fields(self)},
            {f.name: getattr(other, f.name) for f in fields(other)},
        )

    def __hash__(self) -> int:
        msg = f"unhashable type: '{type(self).__name__}'"
        raise TypeError(msg)
