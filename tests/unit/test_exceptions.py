from __future__ import annotations

import numpy as np
import pytest

import plotmux
from plotmux.backends.base import check_export_format, resolve_renderer
from plotmux.backends.registry import get_backend
from plotmux.colors import parse_color
from plotmux.exceptions import (
    BackendNotFoundError,
    ExportError,
    InvalidColorError,
    InvalidSpecError,
    PlotmuxError,
    UnsupportedFormatError,
    UnsupportedSpecError,
)
from plotmux.testing.fixtures import matplotlib_available

######################################
#     Tests for exception hierarchy     #
######################################


@pytest.mark.parametrize(
    "exc_type",
    [
        BackendNotFoundError,
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


def test_resolve_renderer_unknown_raises_plotmux_error() -> None:
    with pytest.raises(PlotmuxError):
        resolve_renderer({}, object(), "test")
    with pytest.raises(NotImplementedError):
        resolve_renderer({}, object(), "test")


def test_check_export_format_unsupported_raises_plotmux_error() -> None:
    with pytest.raises(PlotmuxError):
        check_export_format("bogus", frozenset({"html"}), "test")
    with pytest.raises(ValueError, match="Unsupported export format"):
        check_export_format("bogus", frozenset({"html"}), "test")


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
    from plotmux.export import save
    from plotmux.figure import Figure

    fig = Figure(spec=None, backend_name="does-not-matter", native=None)
    with pytest.raises(PlotmuxError):
        save(fig, "no-suffix")
    with pytest.raises(ValueError, match="Cannot infer the export format"):
        save(fig, "no-suffix")
