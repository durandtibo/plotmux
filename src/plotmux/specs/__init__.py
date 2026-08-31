r"""Contain backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = [
    "BaseSpec",
    "CdfSpec",
    "GridSpec",
    "HistogramSpec",
    "LayerSpec",
    "LineSpec",
    "ScatterSpec",
]

from plotmux.specs.base import BaseSpec
from plotmux.specs.cdf import CdfSpec
from plotmux.specs.grid import GridSpec
from plotmux.specs.histogram import HistogramSpec
from plotmux.specs.layer import LayerSpec
from plotmux.specs.line import LineSpec
from plotmux.specs.scatter import ScatterSpec
