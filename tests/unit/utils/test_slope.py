from __future__ import annotations

import numpy as np

from plotmux.specs import BarSpec, CdfSpec, HistogramSpec, LineSpec, ScatterSpec, SlopeSpec
from plotmux.utils.slope import resolve_slope_xrange

##########################################
#     Tests for resolve_slope_xrange     #
##########################################


def test_resolve_slope_xrange_no_siblings_returns_none() -> None:
    assert resolve_slope_xrange([]) is None


def test_resolve_slope_xrange_only_slope_specs_returns_none() -> None:
    siblings = [SlopeSpec(gradient=1.0, intercept=0.0)]
    assert resolve_slope_xrange(siblings) is None


def test_resolve_slope_xrange_line_spec() -> None:
    siblings = [LineSpec(x=np.arange(10), y=np.arange(10))]
    assert resolve_slope_xrange(siblings) == (0.0, 9.0)


def test_resolve_slope_xrange_histogram_spec() -> None:
    siblings = [HistogramSpec(values=np.arange(101), bins=10)]
    assert resolve_slope_xrange(siblings) == (0.0, 100.0)


def test_resolve_slope_xrange_cdf_spec() -> None:
    siblings = [CdfSpec(values=np.arange(101), nbins=10)]
    assert resolve_slope_xrange(siblings) == (0.0, 100.0)


def test_resolve_slope_xrange_sibling_with_neither_x_nor_values_is_skipped() -> None:
    # Defensive branch: every current data-bound spec type has either ``x``
    # (LineSpec/ScatterSpec/BarSpec) or ``values`` (HistogramSpec/CdfSpec),
    # but a sibling with neither (e.g. a foreign/future spec type) should
    # simply contribute nothing rather than error out.
    class NeitherXNorValues:
        pass

    siblings = [NeitherXNorValues(), LineSpec(x=np.arange(10), y=np.arange(10))]
    assert resolve_slope_xrange(siblings) == (0.0, 9.0)


def test_resolve_slope_xrange_two_values_based_siblings() -> None:
    siblings = [
        HistogramSpec(values=np.arange(101), bins=10),
        CdfSpec(values=np.arange(50, 151), nbins=10),
    ]
    assert resolve_slope_xrange(siblings) == (0.0, 150.0)


def test_resolve_slope_xrange_scatter_spec() -> None:
    siblings = [ScatterSpec(x=np.arange(10), y=np.arange(10))]
    assert resolve_slope_xrange(siblings) == (0.0, 9.0)


def test_resolve_slope_xrange_bar_spec() -> None:
    siblings = [BarSpec(x=np.arange(5), y=np.arange(5))]
    assert resolve_slope_xrange(siblings) == (0.0, 4.0)


def test_resolve_slope_xrange_cdf_spec_with_explicit_bounds() -> None:
    siblings = [CdfSpec(values=np.arange(101), nbins=10, xmin=20, xmax=80)]
    assert resolve_slope_xrange(siblings) == (20.0, 80.0)


def test_resolve_slope_xrange_negative_values() -> None:
    siblings = [LineSpec(x=np.array([-10.0, -5.0, -1.0]), y=np.arange(3))]
    assert resolve_slope_xrange(siblings) == (-10.0, -1.0)


def test_resolve_slope_xrange_single_point_line() -> None:
    siblings = [LineSpec(x=np.array([5.0]), y=np.array([1.0]))]
    assert resolve_slope_xrange(siblings) == (5.0, 5.0)


def test_resolve_slope_xrange_combines_multiple_siblings() -> None:
    siblings = [
        LineSpec(x=np.arange(5, 15), y=np.arange(10)),
        HistogramSpec(values=np.arange(101), bins=10),
        SlopeSpec(gradient=1.0, intercept=0.0),
    ]
    assert resolve_slope_xrange(siblings) == (0.0, 100.0)
