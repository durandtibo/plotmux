from __future__ import annotations

import numpy as np
import pytest

from plotmux.specs import HistogramSpec

####################################
#     Tests for HistogramSpec     #
####################################


def test_histogram_spec_defaults() -> None:
    spec = HistogramSpec(values=np.arange(101))
    assert spec.bins == 30
    assert spec.xmin is None
    assert spec.xmax is None
    assert spec.label is None
    assert spec.density is False
    assert spec.color is None


def test_histogram_spec_custom() -> None:
    spec = HistogramSpec(
        values=np.arange(101),
        bins=10,
        xmin="q0.1",
        xmax="q0.9",
        label="hist",
        density=True,
        color="#ff0000",
    )
    assert spec.bins == 10
    assert spec.xmin == "q0.1"
    assert spec.xmax == "q0.9"
    assert spec.label == "hist"
    assert spec.density is True
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_histogram_spec_empty_values_raises() -> None:
    with pytest.raises(ValueError, match="values must not be empty"):
        HistogramSpec(values=np.array([]))


def test_histogram_spec_non_1d_values_raises() -> None:
    with pytest.raises(ValueError, match="values must be 1-dimensional"):
        HistogramSpec(values=np.arange(12).reshape(3, 4))


def test_histogram_spec_values_coerced_from_list() -> None:
    spec = HistogramSpec(values=[1, 2, 3])
    assert isinstance(spec.values, np.ndarray)
    assert spec.values.tolist() == [1, 2, 3]


def test_histogram_spec_bins_non_integer_raises() -> None:
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=2.5)


def test_histogram_spec_bins_boundary_one() -> None:
    assert HistogramSpec(values=np.arange(101), bins=1).bins == 1


# --- color parsing ---


def test_histogram_spec_color_named() -> None:
    spec = HistogramSpec(values=np.arange(101), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_histogram_spec_color_rgba_tuple() -> None:
    spec = HistogramSpec(values=np.arange(101), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_histogram_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        HistogramSpec(values=np.arange(101), color="not-a-color")


# --- common style ---


def test_histogram_spec_common_style() -> None:
    spec = HistogramSpec(
        values=np.arange(101),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


# --- frozen / error cases ---


def test_histogram_spec_is_frozen() -> None:
    spec = HistogramSpec(values=np.arange(101))
    with pytest.raises(AttributeError):
        spec.bins = 5


@pytest.mark.parametrize("bins", [0, -1, -10])
def test_histogram_spec_invalid_bins(bins: int) -> None:
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=bins)


def test_histogram_spec_xmin_equal_xmax_raises() -> None:
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        HistogramSpec(values=np.arange(101), xmin=5, xmax=5)


def test_histogram_spec_xmin_greater_than_xmax_raises() -> None:
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        HistogramSpec(values=np.arange(101), xmin=10, xmax=0)


def test_histogram_spec_xmin_xmax_quantile_strings_not_checked() -> None:
    # Quantile strings are resolved against the data later by
    # find_range, so they cannot be range-checked at construction time.
    spec = HistogramSpec(values=np.arange(101), xmin="q0.9", xmax="q0.1")
    assert spec.xmin == "q0.9"
    assert spec.xmax == "q0.1"


def test_histogram_spec_xmin_greater_than_xmax_raises_for_numpy_integers() -> None:
    # np.int64/np.int32 are not int subclasses, so the range check must
    # also recognize numpy integer scalars, not just built-in int/float.
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        HistogramSpec(values=np.arange(101), xmin=np.int64(10), xmax=np.int64(5))
