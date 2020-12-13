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

## Part 1: Deliverables

- A url shortener sevice site
- Github Repo for the app

## Design

This is a simple url shortener service in Flask using SQLAlchemy.

With SQLAlchemy I am able to use SQLite as the local testing database
and Postgres as the production database when running on Heroku.

One design decision I made was to not store the shortened url in
the database. Instead I map the database id to the shortened path.

In order to do the mapping I wrote a class called CharacterEncoder
which can be configured to use different character sets. For example
if desired we could remove characters that are commonly mistaken such
as `l` and `I`. This also enabled me to extend the app in an interesting
way later on.

One drawback with this approach is that the generated urls are predictable
and usage could be determined by an external entity. In certain contexts
this could be a security issue.

## Github Actions

This repo is configured with github actions. A push to the main repo
will trigger the tests to run. If the tests pass, the code will automatically
be deployed to the Heroku instance.

## Emoji Extensions 😀

Because I wanted to be a bit creative for the assignment I decided to
extend the basic functionality of the url shortener and instead map
the shortened url's to emojis 😀! I also added tests for this as well.

The currently deployed version uses this, but because it's not
exactly what was requested I wrote the app so that only a configuration
value need to be changed to use the plain ascii version.

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

Alternatively it can be launched with flask:

```
FLASK_APP=app:app flask run
```

Before pushing commits ensure they pass the linter and tests:

```
flake8
python -m pylint tests/
```

## Deployment

The app is currently being run on a free heroku instance with postgres as the database.
This has the following trade offs:

Current Cost: Free
Database is limited to 10,000 records and 1GB of data.

Heroku also has the downside that the app is not always loaded into memory so the
first request in a while may fail or be very slow.

### Configuring Heroku Environment

These steps are not necessary to follow unless creating a new seperate
of the app because it automatically is integrated with github actions.

First install the [heroku cli tool](https://devcenter.heroku.com/articles/heroku-cli).

Ensure that the app has the postgres sql plugin enabled.

To setup the environment variable in the Heroku Environment
that enables the app to use the Heroku config run the following command:

```
heroku config:set ON_HEROKU=1
```
