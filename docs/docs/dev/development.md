# Development Guide

This guide covers setting up your development environment and common development tasks.

## Prerequisites

- Python 3.10 or higher
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
inv install --no-optional-deps

# Install with documentation dependencies
inv install --docs-deps
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
inv unit-test
```

**Run unit tests with coverage:**

```shell
inv unit-test --cov
```

**Run integration tests:**

```shell
inv integration-test
```

**Run a specific test file:**

```shell
pytest tests/unit/test_api.py
```

**Run a specific test:**

```shell
pytest tests/unit/test_api.py::test_hist
```

### Code Quality

**Format code with Black:**

```shell
inv check-format
```

**Run the linter (Ruff):**

```shell
inv check-lint
```

**Format docstrings:**

```shell
inv docformat
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

Then open http://127.0.0.1:8000 in your browser.

**Build documentation without serving:**

```shell
mkdocs build -f docs/mkdocs.yml
```

**Run doctests:**

```shell
inv doctest-src
```

### Type Checking

`plotmux` uses pyright for type checking. You can run type checking locally:

```shell
inv check-types
```

## Project Structure

```
plotmux/
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD workflows
│   └── ISSUE_TEMPLATE/         # Issue templates
├── docs/                       # Documentation
│   ├── docs/                   # Documentation source
│   └── mkdocs.yml              # MkDocs configuration
├── src/plotmux/
│   ├── api.py                  # Public plotting API (hist, cdf, line, scatter, layer, grid)
│   ├── config.py               # Default-backend configuration
│   ├── figure.py                # Figure wrapper
│   ├── export.py                # Figure export utilities
│   ├── exceptions.py            # PlotmuxError hierarchy
│   ├── specs/                  # Backend-agnostic chart specifications
│   ├── backends/                # One package per rendering backend
│   │   ├── base.py             # Backend interface + dispatch helpers
│   │   ├── registry.py         # Backend registration/lookup
│   │   ├── matplotlib/         # Matplotlib backend
│   │   ├── xy/                 # xy backend
│   │   ├── bokeh/               # Bokeh backend
│   │   └── altair/              # Altair backend
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

1. **Create a new branch:**
   ```shell
   git checkout -b feature/my-chart-type
   ```

2. **Add a spec** in `src/plotmux/specs/`, subclassing `BaseSpec` as a frozen dataclass. Specs
   never import a plotting library.

3. **Add a renderer for each backend** (`src/plotmux/backends/matplotlib/`,
   `src/plotmux/backends/xy/`, `src/plotmux/backends/bokeh/`, `src/plotmux/backends/altair/`), and
   register it in that backend's `_RENDERERS` dict.

4. **Export the spec and the public function** from `src/plotmux/specs/__init__.py`,
   `src/plotmux/api.py`, and `src/plotmux/__init__.py`.

5. **Add tests** in `tests/unit/` and `tests/integration/`, mirroring `src/plotmux/`.

6. **Update documentation** in `docs/docs/`.

7. **Run tests and code quality checks:**
   ```shell
   inv unit-test --cov
   pre-commit run --all-files
   ```

8. **Commit and push:**
   ```shell
   git add .
   git commit -m "Add: brief description of the new chart type"
   git push origin feature/my-chart-type
   ```

### Adding a New Backend

See [Adding a Third-Party Backend](../uguide/backends.md#adding-a-third-party-backend) for the
plugin mechanism used by out-of-tree backends, and `src/plotmux/backends/matplotlib/` or
`src/plotmux/backends/xy/` as a reference implementation for a built-in one.

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
   inv unit-test --cov
   ```

6. **Commit and push:**
   ```shell
   git commit -m "Fix: description of bug fix"
   git push origin fix/bug-description
   ```

### Updating Dependencies

```shell
inv update
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
7. **Keep dependencies minimal** — new hard dependencies need a strong justification; prefer an
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
