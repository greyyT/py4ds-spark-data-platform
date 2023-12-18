# Python for Data Science - Spark Data Platform

## Getting started

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in "editable mode" so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

Duplicate the `.env.example` file and rename to `.env`. Then, fill in the values of environment variables in that file.

Start Dagster UI web server:

```bash
dagster dev -h 0.0.0.0
```

Open http://localhost:3000 using your browser to see the project.

## Development

### Adding new Python dependencies:

You can specify new Python dependencies in `setup.py`

### Unit testing

Unit tests are available in `data_platform_tests` directory and you can run tests using pytest:

```bash
pytest data_platform_tests
```

## Deployment with spark cluster

### Build docker images

You need to build 2 images. One for dagster-webserver and dagster-daemon (both use the same image). And one for pipeline.

```bash
docker build -t dagster .
docker build -t pipeline pipeline_data_platform
```