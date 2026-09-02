# plotmux

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

plotmux is a lightweight abstraction layer over Python's plotting libraries. Instead of writing your
visualization code against a specific library like Matplotlib or Plotly, you write it once against
plotmux's unified API, and choose the rendering backend at runtime.

This means you can prototype a figure with a fast, familiar backend, then switch to another one for
interactive dashboards or publication-quality output, without touching your plotting code. Swapping
backends is a one-line configuration change.

plotmux currently supports common figure types such as histograms, empirical CDFs, line plots,
scatter plots, and bar charts, plus layering several charts onto one shared set of axes and laying
out charts as independent panels in a grid, along with export utilities for saving figures to
formats like PNG, SVG, and HTML. Additional backends and chart types are added over time, and the
API is designed so that new backends can be plugged in without breaking existing code.

Typical use cases include libraries and applications that want to stay backend-agnostic, teams that
use different plotting tools across projects, and anyone who wants to avoid rewriting plotting code
every time they change visualization libraries.

## Backends

plotmux ships with five built-in backends, each behind its own optional dependency:
[Matplotlib](https://matplotlib.org/) (`matplotlib`, the default), [`xy`](https://github.com/durandtibo/xy),
[Bokeh](https://bokeh.org/), [Altair](https://altair-viz.github.io/), and [Plotly](https://plotly.com/python/).
A third-party package can
also register its own backend without a change to plotmux's source, via the `plotmux.backends`
entry-point group. See the
[Choosing a Backend](https://durandtibo.github.io/plotmux/uguide/backends/) guide for the full list,
including per-backend export-format support, and for how to write and register a third-party
backend.
