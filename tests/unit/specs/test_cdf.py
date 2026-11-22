from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.primitives import Line
from plotmux.specs import CdfSpec
from plotmux.utils import find_range

##############################
#     Tests for CdfSpec     #
##############################


def test_cdf_spec_defaults() -> None:
    spec = CdfSpec(values=np.arange(101))
    assert spec.nbins is None
    assert spec.xmin is None
    assert spec.xmax is None
    assert spec.label is None
    assert spec.color is None


def test_cdf_spec_custom() -> None:
    spec = CdfSpec(
        values=np.arange(101),
        nbins=10,
        xmin="q0.1",
        xmax="q0.9",
        label="cdf",
        color="#ff0000",
    )
    assert spec.nbins == 10
    assert spec.xmin == "q0.1"
    assert spec.xmax == "q0.9"
    assert spec.label == "cdf"
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_cdf_spec_empty_values_raises() -> None:
    with pytest.raises(ValueError, match="values must not be empty"):
        CdfSpec(values=np.array([]))


def test_cdf_spec_non_1d_values_raises() -> None:
    with pytest.raises(ValueError, match="values must be 1-dimensional"):
        CdfSpec(values=np.arange(12).reshape(3, 4))


def test_cdf_spec_values_coerced_from_list() -> None:
    spec = CdfSpec(values=cast("Any", [1, 2, 3]))
    assert isinstance(spec.values, np.ndarray)
    assert spec.values.tolist() == [1, 2, 3]


def test_cdf_spec_nbins_non_integer_raises() -> None:
    with pytest.raises(ValueError, match="nbins must be a positive integer or None"):
        CdfSpec(values=np.arange(101), nbins=cast("Any", 2.5))


@pytest.mark.parametrize("nbins", [0, -1, -10])
def test_cdf_spec_invalid_nbins(nbins: int) -> None:
    with pytest.raises(ValueError, match="nbins must be a positive integer or None"):
        CdfSpec(values=np.arange(101), nbins=nbins)


def test_cdf_spec_nbins_boundary_one() -> None:
    assert CdfSpec(values=np.arange(101), nbins=1).nbins == 1


def test_cdf_spec_nbins_bool_raises() -> None:
    with pytest.raises(ValueError, match="nbins must be a positive integer or None"):
        CdfSpec(values=np.arange(101), nbins=True)


# --- color parsing ---


def test_cdf_spec_color_named() -> None:
    spec = CdfSpec(values=np.arange(101), color="red")
    assert spec.color == (1.0, 0.0, 0.0, 1.0)


def test_cdf_spec_color_rgba_tuple() -> None:
    spec = CdfSpec(values=np.arange(101), color=(0.1, 0.2, 0.3, 0.4))
    assert spec.color == (0.1, 0.2, 0.3, 0.4)


def test_cdf_spec_invalid_color() -> None:
    with pytest.raises(ValueError, match="Invalid color"):
        CdfSpec(values=np.arange(101), color="not-a-color")


# --- common style ---


# --- frozen / error cases ---


def test_cdf_spec_is_frozen() -> None:
    spec = CdfSpec(values=np.arange(101))
    with pytest.raises(AttributeError):
        cast("Any", spec).nbins = 5


def test_cdf_spec_xmin_equal_xmax_raises() -> None:
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        CdfSpec(values=np.arange(101), xmin=5, xmax=5)


def test_cdf_spec_xmin_greater_than_xmax_raises() -> None:
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        CdfSpec(values=np.arange(101), xmin=10, xmax=0)


def test_cdf_spec_xmin_xmax_quantile_strings_not_checked() -> None:
    # Quantile strings are resolved against the data later by
    # find_range, so they cannot be range-checked at construction time.
    spec = CdfSpec(values=np.arange(101), xmin="q0.9", xmax="q0.1")
    assert spec.xmin == "q0.9"
    assert spec.xmax == "q0.1"


def test_cdf_spec_xmin_greater_than_xmax_raises_for_numpy_integers() -> None:
    # np.int64/np.int32 are not int subclasses, so the range check must
    # also recognize numpy integer scalars, not just built-in int/float.
    with pytest.raises(ValueError, match="xmin must be strictly less than xmax"):
        CdfSpec(
            values=np.arange(101), xmin=cast("Any", np.int64(10)), xmax=cast("Any", np.int64(5))
        )


@pytest.mark.parametrize("alpha", [2.0, -0.1])
def test_cdf_spec_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha must be in the range"):
        CdfSpec(values=np.arange(101), alpha=alpha)


@pytest.mark.parametrize("alpha", [0.0, 1.0])
def test_cdf_spec_alpha_boundary_values(alpha: float) -> None:
    assert CdfSpec(values=np.arange(101), alpha=alpha).alpha == alpha


def test_cdf_spec_does_not_alias_the_input_values() -> None:
    values = np.arange(5, dtype=float)
    spec = CdfSpec(values=values)
    values[0] = 99
    assert spec.values[0] == 0.0


def test_cdf_spec_values_are_read_only() -> None:
    spec = CdfSpec(values=np.arange(5))
    with pytest.raises(ValueError, match="read-only"):
        spec.values[0] = 1


def test_cdf_spec_equal() -> None:
    assert CdfSpec(values=np.arange(5)) == CdfSpec(values=np.arange(5))


def test_cdf_spec_not_equal_with_different_values() -> None:
    assert CdfSpec(values=np.arange(5)) != CdfSpec(values=np.arange(1, 6))


def test_cdf_spec_hash_raises() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'CdfSpec'"):
        hash(CdfSpec(values=np.arange(5)))


######################################
#     Tests for the input policy     #
######################################


def test_cdf_spec_nan_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = CdfSpec(values=np.array([1.0, np.nan, 3.0]))
    assert np.array_equal(spec.values, np.array([1.0, 3.0]))


def test_cdf_spec_inf_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = CdfSpec(values=np.array([1.0, np.inf, 3.0]))
    assert np.array_equal(spec.values, np.array([1.0, 3.0]))


def test_cdf_spec_negative_inf_is_dropped() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = CdfSpec(values=np.array([-np.inf, 2.0, 3.0]))
    assert np.array_equal(spec.values, np.array([2.0, 3.0]))


def test_cdf_spec_warns_with_the_count() -> None:
    with pytest.warns(
        UserWarning,
        match=r"CdfSpec: 3 non-finite value\(s\) \(NaN or inf\) detected in values and filtered out",
    ):
        CdfSpec(values=np.array([1.0, np.nan, np.inf, -np.inf, 2.0]))


def test_cdf_spec_warns_once_per_construction() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        CdfSpec(values=np.array([1.0, np.nan, np.nan, 2.0]))
    assert len(record) == 1


def test_cdf_spec_warning_points_at_the_caller() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        CdfSpec(values=np.array([1.0, np.nan, 2.0]))
    assert record[0].filename == __file__


def test_cdf_spec_finite_values_do_not_warn(recwarn: pytest.WarningsRecorder) -> None:
    CdfSpec(values=np.array([1.0, 2.0, 3.0]))
    assert len(recwarn) == 0


def test_cdf_spec_all_non_finite_raises() -> None:
    with pytest.raises(InvalidSpecError, match="values must contain at least one finite value"):
        CdfSpec(values=np.array([np.nan, np.inf]))


def test_cdf_spec_non_numeric_raises() -> None:
    with pytest.raises(InvalidSpecError, match="values must be numeric"):
        CdfSpec(values=np.array(["a", "b"]))


def test_cdf_spec_dropped_values_are_read_only() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = CdfSpec(values=np.array([1.0, np.nan, 3.0]))
    with pytest.raises(ValueError, match="read-only"):
        spec.values[0] = 1.0


def test_cdf_spec_input_array_is_not_changed() -> None:
    values = np.array([1.0, np.nan, 3.0])
    with pytest.warns(UserWarning, match="NaN or inf"):
        CdfSpec(values=values)
    assert np.array_equal(values, np.array([1.0, np.nan, 3.0]), equal_nan=True)


def test_cdf_spec_quantile_range_uses_the_finite_values() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        spec = CdfSpec(values=np.array([0.0, 10.0, np.inf, np.nan, 5.0]))
    assert find_range(spec.values, "q0.0", "q1.0") == (0.0, 10.0)


def test_cdf_spec_equal_after_filtering() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        a = CdfSpec(values=np.array([1.0, np.nan, 3.0]))
    assert a == CdfSpec(values=np.array([1.0, 3.0]))


#######################################
#     Tests for CdfSpec lowering      #
#######################################


def test_cdf_spec_to_primitives() -> None:
    spec = CdfSpec(values=np.array([3.0, 1.0, 2.0, 4.0]), label="a", color="#ff0000", alpha=0.5)
    assert spec.to_primitives(None) == (
        Line(
            x=np.array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]),
            y=np.array([0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0]),
            infinite=None,
            color=(1.0, 0.0, 0.0, 1.0),
            alpha=0.5,
            linewidth=None,
            linestyle="solid",
            label="a",
        ),
    )


def test_cdf_spec_to_primitives_binned() -> None:
    primitive = cast("Line", CdfSpec(values=np.arange(5.0), nbins=2).to_primitives(None)[0])
    assert primitive.y.tolist() == [0.0, 0.4, 0.4, 1.0, 1.0]


def test_cdf_spec_to_primitives_range_does_not_renormalize() -> None:
    primitive = cast(
        "Line",
        CdfSpec(values=np.array([1.0, 2.0, 3.0, 4.0]), xmin=2, xmax=3).to_primitives(None)[0],
    )
    assert primitive.y.tolist() == [0.25, 0.5, 0.5, 0.75]


def test_cdf_spec_to_primitives_quantile_range() -> None:
    primitive = cast("Line", CdfSpec(values=np.arange(11.0), xmin="q0.5").to_primitives(None)[0])
    assert primitive.x[0] == 5.0


def test_cdf_spec_to_primitives_is_exact_without_nbins() -> None:
    primitive = cast("Line", CdfSpec(values=np.arange(1000.0)).to_primitives(None)[0])
    assert primitive.x.shape == (2000,)


def test_cdf_spec_x_extent() -> None:
    assert CdfSpec(values=np.array([3.0, 1.0, 2.0])).x_extent() == (1.0, 3.0)


def test_cdf_spec_x_extent_explicit_range() -> None:
    assert CdfSpec(values=np.arange(11.0), xmin=2, xmax=4).x_extent() == (2.0, 4.0)


def test_cdf_spec_is_categorical() -> None:
    assert CdfSpec(values=np.arange(3)).is_categorical() is False
