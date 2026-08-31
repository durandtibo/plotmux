r"""Contain utility functions to manage ranges of values."""

from __future__ import annotations

__all__ = ["find_range"]

import numpy as np


def find_range(
    values: np.ndarray,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
) -> tuple[float, float]:
    r"""Find a valid range of values.

    Args:
        values: The array of values used to compute the quantiles.
        xmin: Specifies the lower bound of the range. It can be
            an explicit value, a quantile string such as
            ``"q0.1"`` (i.e. the 10% quantile, where ``"q0"`` is
            the minimum value and ``"q1"`` is the maximum value),
            or ``None`` to use the minimum of ``values``.
        xmax: Specifies the upper bound of the range. It can be
            an explicit value, a quantile string such as
            ``"q0.9"`` (i.e. the 90% quantile, where ``"q0"`` is
            the minimum value and ``"q1"`` is the maximum value),
            or ``None`` to use the maximum of ``values``.

    Returns:
        The range of values as a ``(min, max)`` tuple.
            ``(nan, nan)`` is returned if ``values`` is empty.

    Raises:
        ValueError: if ``xmin`` or ``xmax`` is a string that does
            not have the format ``"q<quantile>"`` where
            ``<quantile>`` is a float in the range ``[0, 1]``, or if
            the resolved lower bound is strictly greater than the
            resolved upper bound (e.g. ``xmin="q0.9", xmax="q0.1"``).

    Example:
        ```pycon
        >>> import numpy as np
        >>> from plotmux.utils import find_range
        >>> data = np.arange(101)
        >>> find_range(data)
        (0, 100)
        >>> find_range(data, xmin=5, xmax=50)
        (5.0, 50.0)
        >>> find_range(data, xmin="q0.1", xmax="q0.9")
        (10.0, 90.0)

        ```
    """
    if values.size == 0:
        return float("nan"), float("nan")
    lo: float = np.nanmin(values).item() if xmin is None else _resolve(values, xmin)
    hi: float = np.nanmax(values).item() if xmax is None else _resolve(values, xmax)
    if lo > hi:
        msg = (
            f"the resolved lower bound must not be greater than the resolved upper "
            f"bound, but received xmin={xmin!r} (resolved to {lo}) and "
            f"xmax={xmax!r} (resolved to {hi})"
        )
        raise ValueError(msg)
    return (lo, hi)


def _resolve(values: np.ndarray, bound: float | str) -> float:
    r"""Resolve a range bound to an explicit float value.

    Args:
        values: The array of values used to compute the quantile
            if ``bound`` is a quantile string.
        bound: The bound to resolve. It can be an explicit value
            or a quantile string such as ``"q0.1"``.

    Returns:
        The resolved bound as a float.
    """
    if isinstance(bound, str):
        return np.nanquantile(values, _parse_quantile(bound)).item()
    return float(bound)


def _parse_quantile(value: str) -> float:
    r"""Parse a quantile string such as ``"q0.1"`` into a float.

    Args:
        value: The quantile string to parse. It must have the
            format ``"q<quantile>"`` where ``<quantile>`` is a
            float in the range ``[0, 1]``.

    Returns:
        The parsed quantile as a float in the range ``[0, 1]``.

    Raises:
        ValueError: if ``value`` does not have the format
            ``"q<quantile>"`` where ``<quantile>`` is a float in
            the range ``[0, 1]``.

    Example:
        ```pycon
        >>> from plotmux.utils.range import _parse_quantile
        >>> _parse_quantile("q0.1")
        0.1

        ```
    """
    if not value.startswith("q"):
        msg = f"Invalid quantile string {value!r}: it must start with 'q'"
        raise ValueError(msg)
    try:
        quantile = float(value[1:])
    except ValueError as err:
        msg = f"Invalid quantile string {value!r}: {value[1:]!r} is not a valid float"
        raise ValueError(msg) from err
    if not 0.0 <= quantile <= 1.0:
        msg = f"Invalid quantile string {value!r}: quantile must be in the range [0, 1]"
        raise ValueError(msg)
    return quantile
