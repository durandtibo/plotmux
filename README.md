# plotmux

plotmux is a lightweight abstraction layer over Python's plotting libraries. Instead of writing your
visualization code against a specific library like Matplotlib or Plotly, you write it once against
plotmux's unified API, and choose the rendering backend at runtime.

This means you can prototype a figure with a fast, familiar backend, then switch to another one for
interactive dashboards or publication-quality output, without touching your plotting code. Swapping
backends is a one-line configuration change.

plotmux currently supports common figure types such as histograms, line plots, and scatter plots,
along with export utilities for saving figures to formats like PNG, SVG, and HTML. Additional
backends and chart types are added over time, and the API is designed so that new backends can be
plugged in without breaking existing code.

Typical use cases include libraries and applications that want to stay backend-agnostic, teams that
use different plotting tools across projects, and anyone who wants to avoid rewriting plotting code
every time they change visualization libraries.
