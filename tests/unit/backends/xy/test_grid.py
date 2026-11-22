from __future__ import annotations

import pytest

from plotmux.testing.fixtures import xy_available
from plotmux.utils.imports import is_xy_available

if is_xy_available():
    import numpy as np
    import xy

    from plotmux.backends.xy.grid import XyGrid, render_grid_html


def _grid(*, ncols: int = 1, title: str | None = None, n: int = 2) -> XyGrid:
    chart = xy.chart(xy.line(np.arange(3.0), np.arange(3.0)))
    return XyGrid(charts=(chart,) * n, ncols=ncols, title=title)


#####################################
#     Tests for render_grid_html    #
#####################################


@xy_available
def test_render_grid_html_embeds_one_iframe_per_chart() -> None:
    assert render_grid_html(_grid(n=3)).count("<iframe") == 3


@xy_available
def test_render_grid_html_includes_title() -> None:
    assert "<h1>my grid</h1>" in render_grid_html(_grid(title="my grid"))


@xy_available
def test_render_grid_html_escapes_title() -> None:
    assert "<h1>a &lt;b&gt;</h1>" in render_grid_html(_grid(title="a <b>"))


@xy_available
def test_render_grid_html_omits_title_heading_when_unset() -> None:
    assert "<h1>" not in render_grid_html(_grid())


@xy_available
def test_render_grid_html_ncols() -> None:
    assert "grid-template-columns: repeat(2, 1fr)" in render_grid_html(_grid(ncols=2))


@pytest.mark.parametrize(("n", "ncols", "nrows"), [(1, 1, 1), (3, 2, 2), (4, 2, 2), (5, 2, 3)])
@xy_available
def test_render_grid_html_rows(n: int, ncols: int, nrows: int) -> None:
    assert f"grid-template-rows: repeat({nrows}, 420px)" in render_grid_html(
        _grid(n=n, ncols=ncols)
    )


@xy_available
def test_render_grid_html_is_a_document() -> None:
    assert render_grid_html(_grid()).startswith("<!doctype html>")
