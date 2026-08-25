r"""Provide ``pytest`` fixtures to skip or require tests based on the
availability of optional dependencies (``altair``, ``bokeh``,
``matplotlib``, ``xy``).

Import a fixture and use it as a test decorator, e.g.
``@matplotlib_available`` skips the test unless ``matplotlib`` is
installed, and ``@matplotlib_not_available`` skips it if ``matplotlib``
is installed.
"""
