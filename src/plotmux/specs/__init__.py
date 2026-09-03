r"""Contain backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = [
    "BarSeries",
    "BarSpec",
    "BaseSpec",
    "CdfSpec",
    "GridSpec",
    "HistogramSpec",
    "LayerSpec",
    "LineSpec",
    "ScatterSpec",
    "SlopeSpec",
    "StackedBarSpec",
]

from plotmux.specs.bar import BarSpec
from plotmux.specs.base import BaseSpec
from plotmux.specs.cdf import CdfSpec
from plotmux.specs.grid import GridSpec
from plotmux.specs.histogram import HistogramSpec
from plotmux.specs.layer import LayerSpec
from plotmux.specs.line import LineSpec
from plotmux.specs.scatter import ScatterSpec
from plotmux.specs.slope import SlopeSpec
from plotmux.specs.stacked_bar import BarSeries, StackedBarSpec
