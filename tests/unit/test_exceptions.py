from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

import plotmux
from plotmux.backends.base import BackendCapabilities
from plotmux.backends.registry import get_backend
from plotmux.colors import parse_color
from plotmux.exceptions import (
    BackendNotFoundError,
    BackendRegistrationError,
    ExportError,
    InvalidColorError,
    InvalidSpecError,
    PlotmuxError,
    UnsupportedFormatError,
    UnsupportedSpecError,
)
from plotmux.export import save
from plotmux.figure import Figure
from plotmux.primitives import Points
from plotmux.scene import AxesScene
from plotmux.testing.fixtures import matplotlib_available

######################################
#     Tests for exception hierarchy     #
######################################


@pytest.mark.parametrize(
    "exc_type",
    [
        BackendNotFoundError,
        BackendRegistrationError,
        UnsupportedSpecError,
        UnsupportedFormatError,
        InvalidColorError,
        InvalidSpecError,
        ExportError,
    ],
)
def test_every_exception_is_a_plotmux_error(exc_type: type[Exception]) -> None:
    assert issubclass(exc_type, PlotmuxError)


def test_backend_not_found_error_is_also_runtime_error() -> None:
    assert issubclass(BackendNotFoundError, RuntimeError)


def test_backend_registration_error_is_also_value_error() -> None:
    assert issubclass(BackendRegistrationError, ValueError)


def test_unsupported_spec_error_is_also_not_implemented_error() -> None:
    assert issubclass(UnsupportedSpecError, NotImplementedError)


def test_unsupported_format_error_is_also_value_error() -> None:
    assert issubclass(UnsupportedFormatError, ValueError)


def test_invalid_color_error_is_also_value_error() -> None:
    assert issubclass(InvalidColorError, ValueError)


def test_invalid_spec_error_is_also_value_error() -> None:
    assert issubclass(InvalidSpecError, ValueError)


def test_export_error_is_also_value_error() -> None:
    assert issubclass(ExportError, ValueError)


def test_get_backend_unknown_raises_plotmux_error() -> None:
    with pytest.raises(PlotmuxError):
        get_backend("does-not-exist")
    with pytest.raises(RuntimeError):
        get_backend("does-not-exist")


def test_unsupported_marker_raises_plotmux_error() -> None:
    caps = BackendCapabilities("test", frozenset(), frozenset(), frozenset(), frozenset())
    scene = AxesScene(primitives=(Points(x=np.arange(2.0), y=np.arange(2.0), marker="x"),))
    with pytest.raises(PlotmuxError):
        caps.check(scene)
    with pytest.raises(NotImplementedError):
        caps.check(scene)


def test_unsupported_format_raises_plotmux_error() -> None:
    caps = BackendCapabilities("test", frozenset({"html"}), frozenset(), frozenset(), frozenset())
    with pytest.raises(PlotmuxError):
        caps.check_format("bogus")
    with pytest.raises(ValueError, match="does not support exporting a figure"):
        caps.check_format("bogus")


def test_parse_color_invalid_raises_plotmux_error() -> None:
    with pytest.raises(PlotmuxError):
        parse_color("not-a-color")
    with pytest.raises(ValueError, match="Invalid color"):
        parse_color("not-a-color")


@matplotlib_available
def test_hist_invalid_bins_raises_plotmux_error() -> None:
    with pytest.raises(PlotmuxError):
        plotmux.hist(np.arange(10), bins=0)
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        plotmux.hist(np.arange(10), bins=0)


def test_export_no_suffix_raises_plotmux_error() -> None:
    fig = Figure(spec=cast("Any", None), backend_name="does-not-matter", native=None)
    with pytest.raises(PlotmuxError):
        save(fig, "no-suffix")
    with pytest.raises(ValueError, match="Cannot infer the export format"):
        save(fig, "no-suffix")
