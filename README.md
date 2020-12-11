# URL Shortener

This is a simple url shortner service in Flask using SQLAlchemy as an ORM
wrapper over an SQLite Database.

I chose to use SQLAlchemy as I've used it before and I know that
if necessary it's pretty easy to swap out the underlying database.
That way it could also be deployed using Postrgres as a backend
with little effort (which might be a requirement for deploying on heroku).

One design decision I made was to not store the shortened url in
the database. Instead I map the database id to the
