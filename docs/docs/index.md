# Home

<p align="center">
    <a href="https://github.com/durandtibo/plotmux/actions/workflows/ci.yaml">
        <img alt="CI" src="https://github.com/durandtibo/plotmux/actions/workflows/ci.yaml/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/plotmux/actions/workflows/nightly-tests.yaml">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/plotmux/actions/workflows/nightly-tests.yaml/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/plotmux/actions/workflows/nightly-package.yaml">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/plotmux/actions/workflows/nightly-package.yaml/badge.svg">
    </a>
    <a href="https://codecov.io/gh/durandtibo/plotmux">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/plotmux/branch/main/graph/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/plotmux/">
        <img alt="Documentation" src="https://github.com/durandtibo/plotmux/actions/workflows/docs.yaml/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/plotmux/dev/">
        <img alt="Documentation" src="https://github.com/durandtibo/plotmux/actions/workflows/docs-dev.yaml/badge.svg">
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="try/except style: tryceratops" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/plotmux/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/plotmux">
    </a>
    <a href="https://pypi.org/project/plotmux/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/plotmux.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/plotmux">
    </a>
    <br/>
    <a href="https://pepy.tech/project/plotmux">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/plotmux">
    </a>
    <a href="https://pepy.tech/project/plotmux">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/plotmux/month">
    </a>
    <br/>
</p>

## Overview

`plotmux` is a lightweight abstraction layer over Python's plotting libraries. Instead of writing
your visualization code against a specific library like Matplotlib, you write it once against
`plotmux`'s unified API, and choose the rendering backend at runtime.

This means you can prototype a figure with a fast, familiar backend, then switch to another one for
interactive dashboards or publication-quality output, without touching your plotting code. Swapping
backends is a one-line configuration change.

**Quick Links:**

- [User Guide](uguide/api.md)
- [Installation](get_started.md)
- [Features](#features)
- [Contributing](#contributing)

## Why plotmux?

Writing plotting code directly against Matplotlib, or any other single library, ties every chart in
your codebase to that library's API. Switching backends later, e.g. to try an interactive one, means
rewriting every call site. `plotmux` solves this with a small, backend-agnostic API:

**Plot with the default backend:**

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=3)
>>> fig.save("histogram.png")  # doctest: +SKIP

```

**Switch backends without changing the plotting code:**

```pycon
>>> import plotmux
>>> with plotmux.backend("xy"):  # doctest: +SKIP
...     fig = plotmux.line([1, 2, 3], [1, 4, 9])
...

```

See the [user guide](uguide/api.md) for detailed examples.

## Features

`plotmux` provides a small, focused set of utilities for backend-agnostic plotting:

### 🎨 **Unified Plotting API**

Plot histograms, line charts, and scatter plots with one API, regardless of the backend that
renders them:

- `plotmux.hist()` for histograms, with optional binning, density, and quantile-based axis ranges
- `plotmux.line()` for line charts
- `plotmux.scatter()` for scatter charts
- Common figure-level styling (`title`, `xlabel`, `ylabel`, `xscale`, `yscale`) shared by every
  chart type

[Learn more →](uguide/api.md)

### 🔀 **Pluggable Backends**

Choose the rendering backend at runtime, and swap it with a one-line change:

- Built-in [Matplotlib](https://matplotlib.org/) backend
- Built-in [`xy`](https://github.com/durandtibo/xy) backend for interactive charts
- Built-in [Bokeh](https://bokeh.org/) backend for interactive, standalone HTML charts
- Built-in [Altair](https://altair-viz.github.io/) (Vega-Lite) backend for declarative,
  standalone HTML charts
- Third-party backends can plug in via a Python entry point, no changes to `plotmux` required

[Learn more →](uguide/backends.md)

### 🧩 **Layering**

Combine multiple charts onto one shared set of axes with `plotmux.layer()`, e.g. overlaying a line
on top of a histogram, without leaving the unified API.

[Learn more →](uguide/layer.md)

### 🔲 **Grid Layouts**

Lay out multiple charts as independent panels in a grid with `plotmux.grid()`, the backend-agnostic
equivalent of Matplotlib's `pyplot.subplots()`. Panels can themselves be layers, since layering and
gridding are independent, composable concerns.

[Learn more →](uguide/grid.md)

### 🖌️ **Backend-Agnostic Colors**

Use the same color syntax everywhere: hex strings, CSS/Matplotlib named colors
(e.g. `"tab:blue"`), or RGB(A) float tuples. `plotmux` normalizes and validates colors once, then
hands each backend its native representation.

[Learn more →](uguide/colors.md)

### 💾 **Export**

Save any figure to a file with `Figure.save()`. The export format is inferred from the file suffix
(e.g. `.png`, `.svg`, `.pdf`), and the parent directory is created automatically.

[Learn more →](uguide/figure.md)

## Contributing

Contributions are welcome! We appreciate bug fixes, feature additions, documentation improvements,
and more. Please check
the [contributing guidelines](https://github.com/durandtibo/plotmux/blob/main/CONTRIBUTING.md) for
details on:

- Setting up the development environment
- Code style and testing requirements
- Submitting pull requests

Whether you're fixing a bug or proposing a new feature, please open an issue first to discuss
your changes.

## API Stability

:warning: **Important**: As `plotmux` is under active development, its API is not yet stable and
may change between releases. We recommend pinning a specific version in your project's dependencies
to ensure consistent behavior.

## License

`plotmux` is licensed under BSD 3-Clause "New" or "Revised" license available
in [LICENSE](https://github.com/durandtibo/plotmux/blob/main/LICENSE)
file.
