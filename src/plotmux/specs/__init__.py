r"""Contain backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = [
    "BarSeries",
    "BarSpec",
    "CdfSpec",
    "FigureSpec",
    "GridSpec",
    "HistogramSpec",
    "LegendLocation",
    "LineSpec",
    "MarkSpec",
    "PanelSpec",
    "ScatterSpec",
    "SlopeSpec",
    "Spec",
    "StackedBarSpec",
]

from plotmux.specs.bar import BarSpec
from plotmux.specs.base import MarkSpec, Spec
from plotmux.specs.cdf import CdfSpec
from plotmux.specs.grid import FigureSpec, GridSpec
from plotmux.specs.histogram import HistogramSpec
from plotmux.specs.line import LineSpec
from plotmux.specs.panel import LegendLocation, PanelSpec
from plotmux.specs.scatter import ScatterSpec
from plotmux.specs.slope import SlopeSpec
from plotmux.specs.stacked_bar import BarSeries, StackedBarSpec
