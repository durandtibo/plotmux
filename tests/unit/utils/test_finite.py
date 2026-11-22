from __future__ import annotations

import numpy as np
import pytest

from plotmux.exceptions import InvalidSpecError
from plotmux.utils.finite import check_no_inf, drop_non_finite

####################################
#     Tests for drop_non_finite     #
####################################


def test_drop_non_finite_all_finite_returns_the_input() -> None:
    values = np.array([1.0, 2.0, 3.0])
    assert drop_non_finite(values, owner="HistogramSpec") is values


def test_drop_non_finite_all_finite_does_not_warn(recwarn: pytest.WarningsRecorder) -> None:
    drop_non_finite(np.array([1.0, 2.0]), owner="HistogramSpec")
    assert len(recwarn) == 0


def test_drop_non_finite_integers_are_finite() -> None:
    assert np.array_equal(drop_non_finite(np.arange(3), owner="HistogramSpec"), np.arange(3))


def test_drop_non_finite_booleans_are_finite() -> None:
    values = np.array([True, False])
    assert np.array_equal(drop_non_finite(values, owner="HistogramSpec"), values)


def test_drop_non_finite_drops_nan() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        result = drop_non_finite(np.array([1.0, np.nan, 3.0]), owner="HistogramSpec")
    assert np.array_equal(result, np.array([1.0, 3.0]))


def test_drop_non_finite_drops_inf() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        result = drop_non_finite(np.array([1.0, np.inf, 3.0]), owner="HistogramSpec")
    assert np.array_equal(result, np.array([1.0, 3.0]))


def test_drop_non_finite_drops_negative_inf() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        result = drop_non_finite(np.array([-np.inf, 2.0]), owner="HistogramSpec")
    assert np.array_equal(result, np.array([2.0]))


def test_drop_non_finite_keeps_the_order() -> None:
    with pytest.warns(UserWarning, match="NaN or inf"):
        result = drop_non_finite(np.array([3.0, np.nan, 1.0, np.inf, 2.0]), owner="CdfSpec")
    assert np.array_equal(result, np.array([3.0, 1.0, 2.0]))


def test_drop_non_finite_does_not_change_the_input() -> None:
    values = np.array([1.0, np.nan])
    with pytest.warns(UserWarning, match="NaN or inf"):
        drop_non_finite(values, owner="HistogramSpec")
    assert np.array_equal(values, np.array([1.0, np.nan]), equal_nan=True)


def test_drop_non_finite_warning_message() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        drop_non_finite(np.array([1.0, np.nan, np.inf, 4.0]), owner="CdfSpec")
    assert [str(w.message) for w in record] == [
        "CdfSpec: 2 non-finite value(s) (NaN or inf) detected in values and filtered out"
    ]


def test_drop_non_finite_warning_uses_the_name() -> None:
    with pytest.warns(UserWarning, match="detected in data and filtered out"):
        drop_non_finite(np.array([1.0, np.nan]), owner="CdfSpec", name="data")


def test_drop_non_finite_warns_once() -> None:
    with pytest.warns(UserWarning, match="NaN or inf") as record:
        drop_non_finite(np.array([1.0, np.nan, np.nan]), owner="CdfSpec")
    assert len(record) == 1


def test_drop_non_finite_all_non_finite_raises() -> None:
    with pytest.raises(
        InvalidSpecError,
        match=r"HistogramSpec: values must contain at least one finite value, but all 2 are NaN or inf",
    ):
        drop_non_finite(np.array([np.nan, np.inf]), owner="HistogramSpec")


@pytest.mark.parametrize("values", [np.array(["a", "b"]), np.array([1 + 1j]), np.array([None])])
def test_drop_non_finite_non_numeric_raises(values: np.ndarray) -> None:
    with pytest.raises(InvalidSpecError, match="HistogramSpec: values must be numeric"):
        drop_non_finite(values, owner="HistogramSpec")


####################################
#     Tests for check_no_inf     #
####################################


def test_check_no_inf_finite() -> None:
    check_no_inf(np.array([1.0, 2.0]), owner="LineSpec", name="y")


def test_check_no_inf_accepts_nan() -> None:
    check_no_inf(np.array([1.0, np.nan]), owner="LineSpec", name="y")


def test_check_no_inf_accepts_integers() -> None:
    check_no_inf(np.arange(3), owner="LineSpec", name="y")


def test_check_no_inf_accepts_categories() -> None:
    check_no_inf(np.array(["a", "b"]), owner="LineSpec", name="x")


def test_check_no_inf_accepts_empty() -> None:
    check_no_inf(np.array([]), owner="LineSpec", name="x")


@pytest.mark.parametrize("value", [np.inf, -np.inf])
def test_check_no_inf_raises(value: float) -> None:
    with pytest.raises(
        InvalidSpecError,
        match=r"LineSpec: y must not contain inf, but received 1 infinite value\(s\)",
    ):
        check_no_inf(np.array([1.0, value]), owner="LineSpec", name="y")


def test_check_no_inf_counts_the_infinite_values() -> None:
    with pytest.raises(InvalidSpecError, match=r"received 2 infinite value\(s\)"):
        check_no_inf(np.array([np.inf, 1.0, -np.inf]), owner="LineSpec", name="y")


def test_check_no_inf_complex() -> None:
    with pytest.raises(InvalidSpecError, match="must not contain inf"):
        check_no_inf(np.array([complex(np.inf, 0)]), owner="LineSpec", name="y")
