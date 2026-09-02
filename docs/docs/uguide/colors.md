# Colors

:book: This page describes `plotmux.colors`, which lets every `color` argument in the unified API
accept the same set of color formats, regardless of the backend rendering the figure.

## Overview

Every `color` argument in `plotmux` (`plotmux.hist(..., color=...)`, `plotmux.line(...,
color=...)`, `plotmux.scatter(..., color=...)`, `plotmux.bar(..., color=...)`) accepts one of:

- a hex string, `"#rrggbb"` or `"#rrggbbaa"`
- a CSS or Matplotlib named color, e.g. `"tab:blue"`, `"crimson"`
- an RGB(A) tuple of floats in `[0, 1]`

Internally, `parse_color()` normalizes any of these into one canonical representation, an RGBA
tuple of floats in `[0, 1]`. Each backend then converts that canonical tuple to whatever its native
call expects. This lookup table is bundled with `plotmux` itself (it mirrors Matplotlib's own
`BASE_COLORS`, `TABLEAU_COLORS`, and `CSS4_COLORS` tables), so named colors resolve correctly even
when Matplotlib is not installed, e.g. when using the `xy` backend alone.

## Parsing a Color

```pycon
>>> from plotmux.colors import parse_color
>>> parse_color("#ff0000")
(1.0, 0.0, 0.0, 1.0)
>>> parse_color("tab:blue")
(0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0)
>>> parse_color((0.5, 0.5, 0.5))
(0.5, 0.5, 0.5, 1.0)

```

An invalid color raises a `ValueError`:

```pycon
>>> from plotmux.colors import parse_color
>>> parse_color("not-a-color")  # doctest: +SKIP
Traceback (most recent call last):
    ...
ValueError: ...

```

## Using Colors in a Plot

```pycon
>>> import plotmux
>>> fig = plotmux.line([1, 2, 3], [1, 4, 9], color="#1f77b4")
>>> fig.save("line.png")  # doctest: +SKIP
>>> fig = plotmux.scatter([1, 2, 3], [1, 4, 9], color=(0.9, 0.1, 0.1, 0.8))
>>> fig.save("scatter.png")  # doctest: +SKIP

```

A spec normalizes its `color` field to the canonical RGBA representation as soon as it is
constructed, so every backend always receives an already-validated color and never has to parse a
raw color itself.

## Predefined Colors and the Default Palette

`plotmux.colors` also exposes a small set of predefined colors, each already a
`parse_color`-normalized RGBA tuple:

```pycon
>>> from plotmux.colors import PRIMARY, SECONDARY, TERTIARY
>>> PRIMARY
(0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0)

```

`DEFAULT_PALETTE` is an ordered tuple of RGBA tuples used to assign successive, visually-distinct
colors to multiple series, or to `plotmux.layer()` children that set no explicit `color`:

```pycon
>>> from plotmux.colors import DEFAULT_PALETTE
>>> len(DEFAULT_PALETTE)
10

```

## What's Next

- [The Plotting API](api.md): use `color` in `hist`, `line`, `scatter`, and `bar`
- [Layering Charts](layer.md): where `DEFAULT_PALETTE` disambiguates children without an explicit
  color
