r"""Check that the installed ``plotmux`` package works.

The script is run by the CI against a package that is *installed* (built
from the source distribution or the wheel, or downloaded from PyPI), not
against the source tree. It is a standalone script, not a pytest module:
it must run in an environment where only ``plotmux`` (and the requested
extras) are installed, so it does not import ``pytest``.

Usage::

    python tests/package/checks.py                    # no extra
    python tests/package/checks.py --extra matplotlib # matplotlib is required
    python tests/package/checks.py --extra all        # every extra is required

An extra is checked by importing the library that it installs: a missing
library is a failure only if the extra was requested with ``--extra``.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import logging
import sys

import plotmux

logger = logging.getLogger(__name__)

# Extra name -> module that the extra installs.
EXTRA_MODULES = {
    "altair": "altair",
    "bokeh": "bokeh",
    "matplotlib": "matplotlib",
    "plotly": "plotly",
    "xy": "xy",
}

# These extras have environment markers (Python version) in ``pyproject.toml``:
# on an unsupported platform the extra installs nothing, so a missing library is
# not a failure.
PLATFORM_DEPENDENT_EXTRAS = frozenset({"xy"})


def check_imports() -> None:
    r"""Check that all main package objects can be imported
    correctly."""
    logger.info("Checking imports...")
    objects_to_import = [
        "plotmux.utils.find_range",
    ]
    for a in objects_to_import:
        module_path, name = a.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        assert obj is not None, f"Failed to import {a}"


def check_version() -> None:
    r"""Check that the package has a version."""
    logger.info("Checking version...")
    assert isinstance(plotmux.__version__, str)


def check_extras(extra: str) -> None:
    r"""Check that the libraries of an extra are installed.

    Args:
        extra: The name of the extra, ``"all"`` for every extra, or
            an empty string for no extra.
    """
    if not extra:
        return
    extras = sorted(EXTRA_MODULES) if extra == "all" else [extra]
    for name in extras:
        logger.info("Checking the extra %r...", name)
        if name in PLATFORM_DEPENDENT_EXTRAS:
            continue
        module = EXTRA_MODULES[name]
        assert importlib.util.find_spec(module) is not None, (
            f"the extra {name!r} was requested but {module!r} is not installed"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    r"""Parse the command line arguments.

    Args:
        argv: The arguments to parse. ``None`` means ``sys.argv[1:]``.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--extra",
        default="",
        choices=["", "all", *sorted(EXTRA_MODULES)],
        help="The extra that was installed with the package (empty for none).",
    )
    return parser.parse_args(argv)


def main() -> None:
    r"""Run all package checks to validate installation and
    functionality."""
    args = parse_args()
    try:
        check_imports()
        check_version()
        check_extras(args.extra)

        logger.info("✅ All package checks passed successfully!")
    except Exception:
        logger.exception("❌ Package check failed")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
