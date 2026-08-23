from __future__ import annotations

import numpy as np
import pytest

from plotmux.core.specs import HistogramSpec


def test_histogram_spec_defaults() -> None:
    spec = HistogramSpec(values=np.arange(101))
    assert spec.bins == 30
    assert spec.xmin is None
    assert spec.xmax is None
    assert spec.label is None
    assert spec.density is False


def test_histogram_spec_custom() -> None:
    spec = HistogramSpec(
        values=np.arange(101),
        bins=10,
        xmin="q0.1",
        xmax="q0.9",
        label="hist",
        density=True,
    )
    assert spec.bins == 10
    assert spec.xmin == "q0.1"
    assert spec.xmax == "q0.9"
    assert spec.label == "hist"
    assert spec.density is True


def test_histogram_spec_is_frozen() -> None:
    spec = HistogramSpec(values=np.arange(101))
    with pytest.raises(AttributeError):
        spec.bins = 5


@pytest.mark.parametrize("bins", [0, -1, -10])
def test_histogram_spec_invalid_bins(bins: int) -> None:
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=bins)
