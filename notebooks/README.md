# Notebooks

## Setup

```shell
uv sync --group jupyter
uv run jupyter lab notebooks/
```

Outputs are stripped automatically on commit via `nbstripout` (configured in
`.pre-commit-config.yaml`), so keep notebooks committed with a clean, re-run-from-top state.
