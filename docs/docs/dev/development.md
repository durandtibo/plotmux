# Development Guide

This guide covers setting up your development environment and common development tasks.

## Prerequisites

- Python 3.11 or higher
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- Git for version control
- Basic knowledge of Python and testing

## Initial Setup

### 1. Fork and Clone

```shell
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/plotmux.git
cd plotmux
```

### 2. Set Up Virtual Environment

The project uses `uv` for dependency management. First, install `uv` if you don't have it:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create and set up the virtual environment:

```shell
make setup-venv
```

This will create a virtual environment and install all dependencies, including development tools
and documentation dependencies.

Activate the virtual environment:

```shell
source .venv/bin/activate
```

### 3. Install Dependencies

If you already have a virtual environment and just want to install dependencies:

```shell
# Install core dependencies
inv env.install --no-optional-deps --groups ""

# Install with documentation dependencies
inv env.install
```

### 4. Set Up Pre-commit Hooks

```shell
pre-commit install
```

This will automatically run code quality checks before each commit.

## Development Workflow

### Running Tests

**Run all unit tests:**

```shell
inv test.unit
```

**Run unit tests with coverage:**

```shell
inv test.unit --cov
```

**Run integration tests:**

```shell
inv test.integration
```

**Run a specific test file:**

```shell
pytest tests/unit/test_api.py
```

**Run a specific test:**

```shell
pytest tests/unit/test_api.py::test_hist
```

### Invoke Tasks

The predefined `inv` tasks come from [invoke-tasklib](https://github.com/durandtibo/invoke-tasklib),
configured in `invoke.yaml` (`tasks.py` only calls `make_ns()` and adds the `test.check-notebooks`
task). List the tasks and the resolved configuration with:

```shell
inv --list
inv config.show
```

`inv check` runs the main read-only checks and `inv fix` fixes the lint and format issues.

### Code Quality

**Check the code format (Ruff):**

```shell
inv format.check-python
```

**Run the linter (Ruff):**

```shell
inv lint.check-python
```

**Format docstrings:**

```shell
inv format.check-docstrings
```

**Run all pre-commit checks:**

```shell
pre-commit run --all-files
```

### Documentation

**Build documentation locally:**

```shell
mkdocs serve -f docs/mkdocs.yml
```

Then open <http://127.0.0.1:8000> in your browser.

**Build documentation without serving:**

```shell
mkdocs build -f docs/mkdocs.yml
```

**Run doctests:**

```shell
inv test.doctest
```

### Type Checking

`plotmux` uses ty and pyright for type checking. You can run both locally:

```shell
inv types.check --complete
```

`inv types.check` runs only ty, which is faster.

## Project Structure

```text
plotmux/
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD workflows
│   └── ISSUE_TEMPLATE/         # Issue templates
├── docs/                       # Documentation
│   ├── docs/                   # Documentation source
│   └── mkdocs.yml              # MkDocs configuration
├── src/plotmux/
│   ├── api.py                  # Public plotting API (hist, bar, stacked_bar, cdf, line,
│   │                            #   scatter, slope, layer, grid)
│   ├── config.py               # Default-backend configuration
│   ├── figure.py                # Figure wrapper
│   ├── export.py                # Figure export utilities
│   ├── exceptions.py            # PlotmuxError hierarchy
│   ├── specs/                  # Backend-agnostic marks, panels and grids
│   ├── primitives.py           # The three drawing primitives (Bars, Line, Points)
│   ├── scene.py                # build_scene(): lowers a spec to primitives
│   ├── backends/                # One package per rendering backend
│   │   ├── base.py             # Backend interface + BackendCapabilities
│   │   ├── registry.py         # Backend registration/lookup
│   │   ├── matplotlib/         # Matplotlib backend
│   │   ├── xy/                 # xy backend
│   │   ├── bokeh/               # Bokeh backend
│   │   ├── altair/              # Altair backend
│   │   └── plotly/              # Plotly backend
│   ├── colors/                  # Color parsing and palettes
│   ├── testing/                 # pytest fixtures for downstream users
│   └── utils/                   # Small utilities (ranges, optional imports)
├── tests/                      # Test files
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── pyproject.toml               # Project configuration
├── uv.lock                      # Locked dependencies
├── LICENSE                      # License file
├── README.md                    # Project README
└── DESIGN.md                    # Design document
```

## Common Development Tasks

### Adding a New Chart Type

A chart type is one **mark**: a `MarkSpec` subclass that lowers itself to the primitives (`Bars`,
`Line`, `Points`). If the chart is a composition of those primitives (a box plot is bars and lines),
no backend changes.

1. **Create a new branch:**

   ```shell
   git checkout -b feature/my-chart-type
   ```

2. **Add a mark** in `src/plotmux/specs/`, subclassing `MarkSpec` as a frozen dataclass
   (`@dataclass(frozen=True, eq=False)`). Specs never import a plotting library. Validate the input
   in `__post_init__` (call `super().__post_init__()` first, which validates `label`, `color` and
   `alpha`), raise `InvalidSpecError`, and copy the arrays with `to_readonly_array`. Implement:

   - `to_primitives(extent)`: the tuple of primitives to draw, with the numbers resolved (bins,
     steps, bases, widths). `extent` is the resolved x extent of the panel; a mark with no data of
     its own sets `requires_extent = True` and uses it.
   - `x_extent()`: the `(min, max)` of its x data, or `None` (the default) if it has none.
   - `is_categorical()`: `True` for string x data, `False` for numeric x data, `None` (the default)
     if it has none, so that a panel can refuse to mix them.

3. **Export the mark and the public function** from `src/plotmux/specs/__init__.py`,
   `src/plotmux/api.py` (build the mark and call `_render_mark(mark, panel)`; add the function name
   to `_check_options`) and `src/plotmux/__init__.py`.

4. **Add tests**: `tests/unit/specs/test_<mark>.py` (validation, and `to_primitives` against a
   literal tuple of primitives), the API test, and one entry in the `MARKS` table of
   `tests/integration/conformance/test_conformance.py`, which checks that the five backends draw
   what the scene says, standalone, in a layer and in a grid.

5. **Update documentation** in `docs/docs/`.

6. **Run tests and code quality checks:**

   ```shell
   inv test.unit --cov
   pre-commit run --all-files
   ```

7. **Commit and push:**

   ```shell
   git add .
   git commit -m "Add a box plot chart type"
   git push origin feature/my-chart-type
   ```

If the chart needs a new primitive, add it to `plotmux/primitives.py` and one `draw_<primitive>` to
each backend: that is the exception, not the rule.

### Adding a New Backend

A backend is two modules in `src/plotmux/backends/<name>/`:

- `backend.py`: a `Backend` subclass with `capabilities()` (the export formats of a figure and of a
  grid, the legend locations and the markers it honors), `draw(scene)` (draw each primitive of the
  `AxesScene`, apply the axes style, compose a `GridScene`) and `save(native, path, fmt)`, and
  `show`/`mimebundle` if the library needs them. `draw_bars`, `draw_line` and `draw_points` are the
  three functions that translate a primitive.
- `style.py`: `apply_style(native, scene)` (title, labels, scales, limits, background, legend) and
  the translation tables (colors, line styles, markers, legend locations).

Then register it in the built-in table of `src/plotmux/backends/registry.py` (and add its
`is_<name>_available` helper and its extra), or ship it as an independent package with an entry
point, see [Adding a Third-Party Backend](../uguide/backends.md#adding-a-third-party-backend). Add
it to the `BACKENDS` list of `tests/integration/conformance/test_conformance.py` with an
`extract_<name>` function that reads the primitives back from the native figure:
the conformance test is the executable definition of "the same chart on every backend".
`src/plotmux/backends/matplotlib/` and `src/plotmux/backends/xy/` are reference implementations.

### Fixing a Bug

1. **Create a branch:**

   ```shell
   git checkout -b fix/bug-description
   ```

2. **Write a failing test** that reproduces the bug

3. **Fix the bug**

4. **Verify the test passes:**

   ```shell
   pytest tests/unit/path/to/test.py
   ```

5. **Run the full test suite:**

   ```shell
   inv test.unit --cov
   ```

6. **Commit and push:**

   ```shell
   git commit -m "Fix: description of bug fix"
   git push origin fix/bug-description
   ```

### Updating Dependencies

```shell
inv env.update
```

Dependencies are managed in `pyproject.toml` and locked in `uv.lock`.

## Testing Guidelines

### Writing Good Tests

1. **Use descriptive names:**

   ```python
   def test_hist_returns_figure(): ...


   def test_hist_raises_error_for_non_positive_bins(): ...
   ```

2. **Test edge cases:**
   - Empty arrays
   - `None` values
   - Invalid colors or ranges
   - Every combination of chart type x backend x export format

3. **Use `plotmux.testing` fixtures to skip tests based on installed backends:**

   ```python
   from plotmux.testing import matplotlib_available


   @matplotlib_available
   def test_hist_with_matplotlib_backend():
       fig = plotmux.hist([1, 2, 3], backend="matplotlib")
       assert fig.backend_name == "matplotlib"
   ```

4. **Test both success and failure cases:**

   ```python
   def test_success_case():
       assert plotmux.hist([1, 2, 3]) is not None


   def test_failure_case():
       with pytest.raises(ValueError, match="bins must be a positive integer"):
           HistogramSpec(values=np.arange(10), bins=0)
   ```

## Continuous Integration

The project uses GitHub Actions for CI. Workflows are in `.github/workflows/`:

- **CI**: Runs on every push and PR
  - Linting
  - Tests
  - Coverage

- **Documentation**: Builds and deploys docs
  - Builds on every push
  - Deploys on release

- **Nightly Tests**: Tests against latest dependencies
  - Runs daily
  - Tests multiple Python versions

## Best Practices

1. **Write tests first** (TDD approach when possible)
2. **Keep PRs focused** on a single feature or fix
3. **Update documentation** for user-facing changes
4. **Run pre-commit hooks** before committing
5. **Write clear commit messages**
6. **Add docstrings, with a runnable `pycon` example, to all public APIs**
7. **Keep dependencies minimal**: new hard dependencies need a strong justification; prefer an
   optional extra
8. **Follow existing code style**, in particular the separation between specs (backend-agnostic)
   and backends (library-specific), see [Architecture](architecture.md)

## Code Review Checklist

Before submitting a PR, ensure:

- [ ] All tests pass locally
- [ ] Code coverage is maintained or improved
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Code follows project style
- [ ] No unnecessary dependencies added
- [ ] Examples are provided for new features
- [ ] Edge cases are tested

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
