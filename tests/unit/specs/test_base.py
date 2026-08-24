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
