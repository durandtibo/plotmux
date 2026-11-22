from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.specs import HistogramSpec
from plotmux.utils import find_range

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
    spec = HistogramSpec(values=cast("Any", [1, 2, 3]))
    assert isinstance(spec.values, np.ndarray)
    assert spec.values.tolist() == [1, 2, 3]


def test_histogram_spec_bins_non_integer_raises() -> None:
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=cast("Any", 2.5))


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
        cast("Any", spec).bins = 5


@pytest.mark.parametrize("bins", [0, -1, -10])
def test_histogram_spec_invalid_bins(bins: int) -> None:
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=bins)


def test_histogram_spec_bins_bool_raises() -> None:
    # bool is an Integral subclass, but it must not be accepted as bins.
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        HistogramSpec(values=np.arange(101), bins=True)


def test_histogram_spec_bins_numpy_integer_accepted() -> None:
    spec = HistogramSpec(values=np.arange(101), bins=cast("Any", np.int64(5)))
    assert spec.bins == 5


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
        HistogramSpec(
            values=np.arange(101), xmin=cast("Any", np.int64(10)), xmax=cast("Any", np.int64(5))
        )


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_histogram_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        HistogramSpec(values=np.arange(101), alpha=alpha)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_histogram_spec_alpha_boundary_values(alpha: float) -> None:
    assert HistogramSpec(values=np.arange(101), alpha=alpha).alpha == alpha


def test_histogram_spec_xmin_only_explicit_does_not_raise() -> None:
    spec = HistogramSpec(values=np.arange(101), xmin=5)
    assert spec.xmin == 5
    assert spec.xmax is None


def test_histogram_spec_ymin_greater_than_ymax_raises() -> None:
    with pytest.raises(ValueError, match="ymin must not be greater than ymax"):
        HistogramSpec(values=np.arange(101), ymin=10, ymax=0)


def test_histogram_spec_does_not_alias_the_input_values() -> None:
    values = np.arange(5, dtype=float)
    spec = HistogramSpec(values=values)
    values[0] = 99
    assert spec.values[0] == 0.0


def test_histogram_spec_values_are_read_only() -> None:
    spec = HistogramSpec(values=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.values[0] = 1


def test_histogram_spec_equal() -> None:
    assert HistogramSpec(values=np.arange(5)) == HistogramSpec(values=np.arange(5))


def test_histogram_spec_not_equal_with_different_values() -> None:
    assert HistogramSpec(values=np.arange(5)) != HistogramSpec(values=np.arange(1, 6))


def test_histogram_spec_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'HistogramSpec'"):
        hash(HistogramSpec(values=np.arange(5)))


######################################
#     Tests for the input policy     #
######################################


def test_histogram_spec_nan_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = HistogramSpec(values=np.array([1.0, np.nan, 3.0]))
    assert np.array_equal(spec.values, np.array([1.0, 3.0]))


def test_histogram_spec_inf_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = HistogramSpec(values=np.array([1.0, np.inf, 3.0]))
    assert np.array_equal(spec.values, np.array([1.0, 3.0]))


def test_histogram_spec_negative_inf_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = HistogramSpec(values=np.array([-np.inf, 2.0, 3.0]))
    assert np.array_equal(spec.values, np.array([2.0, 3.0]))


def test_histogram_spec_warns_with_the_count() -> None:
    with pytest.warns(
        UserWarning,
        match=r"HistogramSpec: 3 non-finite value\(s\) \(NaN or inf\) detected in values and filtered out",
    ):
        HistogramSpec(values=np.array([1.0, np.nan, np.inf, -np.inf, 2.0]))


def test_histogram_spec_warns_once_per_construction() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        HistogramSpec(values=np.array([1.0, np.nan, np.nan, 2.0]))
    assert len(record) == 1


def test_histogram_spec_warning_points_at_the_caller() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        HistogramSpec(values=np.array([1.0, np.nan, 2.0]))
    assert record[0].filename == __file__


def test_histogram_spec_finite_values_do_not_warn(recwarn: pytest.WarningsRecorder) -> None:
    HistogramSpec(values=np.array([1.0, 2.0, 3.0]))
    assert len(recwarn) == 0


def test_histogram_spec_all_non_finite_raises() -> None:
    with pytest.raises(InvalidSpecError, match="values must contain at least one finite value"):
        HistogramSpec(values=np.array([np.nan, np.inf]))


def test_histogram_spec_non_numeric_raises() -> None:
    with pytest.raises(InvalidSpecError, match="values must be numeric"):
        HistogramSpec(values=np.array(["a", "b"]))


def test_histogram_spec_dropped_values_are_read_only() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = HistogramSpec(values=np.array([1.0, np.nan, 3.0]))
    with pytest.raises(ValueError, match="read-only"):
        spec.values[0] = 1.0


def test_histogram_spec_input_array_is_not_changed() -> None:
    values = np.array([1.0, np.nan, 3.0])
    with pytest.warns(UserWarning, match="NaN or inf"):
        HistogramSpec(values=values)
    assert np.array_equal(values, np.array([1.0, np.nan, 3.0]), equal_nan=True)


def test_histogram_spec_quantile_range_uses_the_finite_values() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = HistogramSpec(values=np.array([0.0, 10.0, np.inf, np.nan, 5.0]))
    assert find_range(spec.values, "q0.0", "q1.0") == (0.0, 10.0)


def test_histogram_spec_equal_after_filtering() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        a = HistogramSpec(values=np.array([1.0, np.nan, 3.0]))
    assert a == HistogramSpec(values=np.array([1.0, 3.0]))
