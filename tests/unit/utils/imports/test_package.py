from __future__ import annotations

from plotmux.utils.imports.package import decorator_package_available


def add_one(x: int, *, offset: int = 0) -> int:
    r"""Add one to the input."""
    return x + 1 + offset


#################################################
#     Tests for decorator_package_available     #
#################################################


def test_decorator_package_available_true() -> None:
    assert decorator_package_available(add_one, lambda: True)(1) == 2


def test_decorator_package_available_true_kwargs() -> None:
    assert decorator_package_available(add_one, lambda: True)(1, offset=10) == 12


def test_decorator_package_available_false() -> None:
    assert decorator_package_available(add_one, lambda: False)(1) is None


def test_decorator_package_available_evaluates_condition_at_call_time() -> None:
    state = {"available": False}
    wrapped = decorator_package_available(add_one, lambda: state["available"])
    state["available"] = True
    assert wrapped(1) == 2
