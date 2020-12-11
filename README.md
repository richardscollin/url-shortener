# URL Shortener

## Installation

First set up a virtual environment using the venv module:

```
python3 -m venv myenv
```

Activate the virtual environment:

```
source myenv/bin/activate
```

Then install the project using pip:

```
pip install -r requirements.txt
```

The webserver can then be launched with
the gunicorn runner:

```
gunicorn app:app
```

Alternatively it can be launched directly with python:

```
python app.py
```

Before pushing commits ensure they pass the linter and tests:

```
flake8
python -m pylint tests/
```

## Design

This is a simple url shortner service in Flask using SQLAlchemy as an ORM
wrapper over an SQLite Database.

I chose to use SQLAlchemy as I've used it before and I know that
if necessary it's pretty easy to swap out the underlying database.
That way it could also be deployed using Postrgres as a backend
with little effort (which might be a requirement for deploying on heroku).

One design decision I made was to not store the shortened url in
the database. Instead I map the database id to the
