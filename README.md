# Building Shorten URL service

Context:
Suppose you start working your first project is building a url shortener service. This application should behave similarly to https://tinyurl.com or https://bitly.com.

Requirements:

- The length of the shortened path should start from 2 letters and be unique.
- The website should be able to redirect the user to the original url.

### Part 1: Planning the deliveries

Please describe in English how you would plan the project and a high level design of the architecture. What principles or design practices would you consider incorporating into the process and technology? You may include diagrams. You do not need to write any code for this part of the problem.

### Part 2: Implement url registration and redirection.

Requirements:

- Make sure the submission runs.
- Please write test cases for the implemented features..
- Provide instructions for setup and launch (in a README file).

Please note that you can use your familiar stack for this part.

## Design

This is a simple url shortner service in Flask using SQLAlchemy as an ORM
wrapper over an SQLite Database.

I chose to use SQLAlchemy as I've used it before and I know that
if necessary it's pretty easy to swap out the underlying database.
That way it could also be deployed using Postrgres as a backend
with little effort (which might be a requirement for deploying on heroku).

One design decision I made was to not store the shortened url in
the database. Instead I map the database id to the

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
