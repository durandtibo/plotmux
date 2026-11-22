r"""Define the tasks that are executed with invoke."""

from __future__ import annotations

from invoke import Context, Task
from invoke_tasklib import make_ns

__all__ = ["ns"]

ns = make_ns()


def check_notebooks(c: Context) -> None:
    r"""Execute the notebooks and check that they run without errors."""
    c.run(
        "jupyter nbconvert --to notebook --execute --stdout notebooks/*.ipynb",
        pty=True,
    )


ns.collections["test"].add_task(Task(check_notebooks, name="check-notebooks"))
