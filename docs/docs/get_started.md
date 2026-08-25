# Get Started

We highly recommend installing
`plotmux` in
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
to avoid dependency conflicts.

## Using uv (recommended)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package installer and resolver:

```shell
uv pip install plotmux
```

**Install with a specific backend:**

```shell
uv pip install plotmux[matplotlib]
uv pip install plotmux[xy]
uv pip install plotmux[bokeh]
uv pip install plotmux[altair]
```

**Install with all optional dependencies:**

```shell
uv pip install plotmux[matplotlib,xy,bokeh,altair]
```

## Using pip

Alternatively, you can use `pip`:

```shell
pip install plotmux
```

**Install with a specific backend:**

```shell
pip install plotmux[matplotlib]
pip install plotmux[xy]
pip install plotmux[bokeh]
pip install plotmux[altair]
```

## Installing from source

To install `plotmux` from source, you can follow the steps below.

First, clone the git repository:

```shell
git clone git@github.com:durandtibo/plotmux.git
cd plotmux
```

**Note**: `plotmux` requires Python 3.10 or higher. The `xy` backend additionally requires
Python 3.11 or higher.

It is recommended to create a virtual environment (this step is optional).
To create a virtual environment, you can use the following command:

```shell
make setup-venv
```

This command automatically creates a virtual environment using [`uv`](https://docs.astral.sh/uv/).
When the virtual environment is created, you can activate it with the following command:

```shell
source .venv/bin/activate
```

Then, you should install the required packages to use `plotmux` with the following command:

```shell
inv install --docs-deps
```

This command will install all the required packages. You can also use this command to update the
required packages. This command will check if there is a more recent package available and will
install it. Finally, you can test the installation with the following command:

```shell
inv unit-test --cov
```

## Dependencies

`plotmux` only has two hard dependencies: [NumPy](https://numpy.org/) and
[`coola`](https://github.com/durandtibo/coola). Each rendering backend is an optional dependency,
so the core package (specs, registry, configuration, public API) always imports cleanly, even with
no plotting library installed. Only the backend you actually use needs to be installed.

| Extra          | Installs                                     | Notes                       |
|----------------|-----------------------------------------------|------------------------------|
| `matplotlib`   | [Matplotlib](https://matplotlib.org/)         | Python 3.10+                 |
| `xy`           | [`xy`](https://github.com/durandtibo/xy)      | Python 3.11+                 |

## Quick check

Once installed, you can verify the installation with a minimal example:

```pycon
>>> import plotmux
>>> fig = plotmux.hist([1, 2, 2, 3, 3, 3], bins=3)
>>> fig.save("histogram.png")  # doctest: +SKIP

```

See the [user guide](uguide/api.md) to learn more about `plotmux`'s API.
