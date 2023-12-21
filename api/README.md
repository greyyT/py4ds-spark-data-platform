# Python for Data Science - Movies Related API

## Getting started

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in "editable mode" so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

Start FastAPI serving our project's models:

```bash
python3 main.py
```

Open http://localhost:8000/docs using your browser to test out all of the endpoints.

## API Endpoints

### POST /recommend-movies

Schema:

```json
{
    name: "Monsters, Inc.",
}
```

This endpoint returns a list of recommended movies based on the name of the movie you provide.

### POST /predict-comment

Schema:

```json
{
    comment: "This movie was great!",
}
```

This endpoint returns a boolean value indicating whether the comment is positive or negative.