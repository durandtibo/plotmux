from __future__ import annotations

from dataclasses import dataclass

import pytest

from plotmux.specs.base import BaseSpec


@dataclass(frozen=True)
class FakeSpec(BaseSpec):
    value: int = 0


def test_base_spec_is_dataclass() -> None:
    spec = FakeSpec(value=42)
    assert spec.value == 42


def test_base_spec_is_frozen() -> None:
    spec = FakeSpec(value=42)
    with pytest.raises(AttributeError):
        spec.value = 43


def test_base_spec_default_style() -> None:
    spec = FakeSpec(value=42)
    assert spec.title is None
    assert spec.xlabel is None
    assert spec.ylabel is None
    assert spec.xscale == "linear"
    assert spec.yscale == "linear"


def test_base_spec_custom_style() -> None:
    spec = FakeSpec(value=42, title="t", xlabel="x", ylabel="y", xscale="log", yscale="log")
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"
