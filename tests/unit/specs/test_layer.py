from __future__ import annotations

import numpy as np
import pytest

from plotmux.colors.palette import DEFAULT_PALETTE
from plotmux.specs import HistogramSpec, LayerSpec, LineSpec, ScatterSpec

################################
#     Tests for LayerSpec     #
################################


def test_layer_spec_layers() -> None:
    hist_spec = HistogramSpec(values=np.arange(101), bins=10)
    line_spec = LineSpec(x=np.arange(10), y=np.arange(10))
    spec = LayerSpec(layers=(hist_spec, line_spec))
    assert len(spec.layers) == 2
    assert spec.layers[0].bins == 10
    np.testing.assert_array_equal(spec.layers[0].values, hist_spec.values)
    np.testing.assert_array_equal(spec.layers[1].x, line_spec.x)
    np.testing.assert_array_equal(spec.layers[1].y, line_spec.y)


def test_layer_spec_assigns_default_colors_to_uncolored_children() -> None:
    hist_spec = HistogramSpec(values=np.arange(101), bins=10)
    line_spec = LineSpec(x=np.arange(10), y=np.arange(10))
    spec = LayerSpec(layers=(hist_spec, line_spec))
    assert spec.layers[0].color == DEFAULT_PALETTE[0]
    assert spec.layers[1].color == DEFAULT_PALETTE[1]


def test_layer_spec_keeps_explicit_colors_and_only_cycles_palette_over_the_rest() -> None:
    red_line = LineSpec(x=np.arange(10), y=np.arange(10), color="#ff0000")
    scatter = ScatterSpec(x=np.arange(10), y=np.arange(10))
    hist_spec = HistogramSpec(values=np.arange(101), bins=10)
    spec = LayerSpec(layers=(red_line, scatter, hist_spec))
    assert spec.layers[0].color == (1.0, 0.0, 0.0, 1.0)
    assert spec.layers[1].color == DEFAULT_PALETTE[0]
    assert spec.layers[2].color == DEFAULT_PALETTE[1]


def test_layer_spec_palette_cycles_when_children_exceed_palette_size() -> None:
    children = tuple(
        ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(len(DEFAULT_PALETTE) + 1)
    )
    spec = LayerSpec(layers=children)
    assert spec.layers[0].color == DEFAULT_PALETTE[0]
    assert spec.layers[-1].color == DEFAULT_PALETTE[0]


def test_layer_spec_grid_child_without_color_field_is_left_untouched() -> None:
    # GridSpec has no ``color`` field: ``getattr(child, "color", "unset")``
    # falls back to "unset" (not None), so it must not be treated as a
    # color-carrying child needing a palette slot.
    from plotmux.specs import GridSpec

    grid_child = GridSpec(cells=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    line_spec = LineSpec(x=np.arange(10), y=np.arange(10))
    spec = LayerSpec(layers=(grid_child, line_spec))
    assert spec.layers[0] is grid_child
    assert spec.layers[1].color == DEFAULT_PALETTE[0]


def test_layer_spec_single_child() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    assert len(spec.layers) == 1


def test_layer_spec_many_children() -> None:
    children = tuple(ScatterSpec(x=np.arange(10), y=np.arange(10)) for _ in range(5))
    spec = LayerSpec(layers=children)
    assert len(spec.layers) == 5


def test_layer_spec_common_style() -> None:
    spec = LayerSpec(
        layers=(LineSpec(x=np.arange(10), y=np.arange(10)),),
        title="t",
        xlabel="x",
        ylabel="y",
        xscale="log",
        yscale="log",
    )
    assert spec.title == "t"
    assert spec.xlabel == "x"
    assert spec.ylabel == "y"
    assert spec.xscale == "log"
    assert spec.yscale == "log"


# --- frozen / error cases ---


def test_layer_spec_is_frozen() -> None:
    spec = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(AttributeError):
        spec.layers = ()


def test_layer_spec_empty_layers_raises() -> None:
    with pytest.raises(ValueError, match="layers must contain at least one spec"):
        LayerSpec(layers=())


def test_layer_spec_nested_layer_raises() -> None:
    inner = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    with pytest.raises(ValueError, match="layers must not contain a LayerSpec"):
        LayerSpec(layers=(inner,))


def test_layer_spec_nested_layer_among_other_children_raises() -> None:
    inner = LayerSpec(layers=(LineSpec(x=np.arange(10), y=np.arange(10)),))
    other = ScatterSpec(x=np.arange(10), y=np.arange(10))
    with pytest.raises(ValueError, match="layers must not contain a LayerSpec"):
        LayerSpec(layers=(other, inner))
