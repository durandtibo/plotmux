r"""Contain backend-agnostic chart specifications."""

from __future__ import annotations

__all__ = ["BaseSpec", "HistogramSpec", "LineSpec", "ScatterSpec"]

from plotmux.specs.base import BaseSpec
from plotmux.specs.histogram import HistogramSpec
from plotmux.specs.line import LineSpec
from plotmux.specs.scatter import ScatterSpec
