# -*- coding: utf-8 -*-
import os
import re
import logging
from flask import abort, Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

class AppError(Exception):
    """Wrap base Exception class for app custom errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

if os.environ.get("ON_HEROKU"):
    app.config.from_object('config.HerokuConfig')
else:
    app.config.from_object('config.DebugConfig')

db = SQLAlchemy(app)
from models import Url
db.create_all()

@ app.route("/", methods=["GET", "POST"])
def index():
    added = None
    urls = db.session.query(Url).order_by(Url.id.desc()).limit(10)

    if request.method == "POST":
        try:
            url = request.form.get("url")
            if not url:
                raise AppError("Required post parameter: url missing.")

            added = create_link(url)

        except AppError as e:
            return render_template("index.html", base_url=request.host, error=e, urls=urls)

    return render_template("index.html", base_url=request.host, url=added, urls=urls)


def create_link(url):
    """
    :param: url: string - user provided url to shorten
    @returns string - the shortened url slug
    :throws: AppError on any failure i.e. database
    """
    try:
        # prefix path with http:// if it doesn't already start with
        # http:// or https://
        # Note: we do this here instead of in the url validation function
        # to ensure the exists query works properly
        if not re.match(r"https?://", url):
            url = "http://" + url

        exists = Url.query.filter_by(href=url).first()
        if exists:
            return exists

        new_link = Url(href=url)
        db.session.add(new_link)
        db.session.commit()

        return new_link
    except SQLAlchemyError as e:
        # catch and rethrow exceptions with custom messages
        raise AppError("SQLAlchemyError: " + str(e))


@ app.route("/<slug>")
def redirect_shortened_url(slug):
    if slug in {"favicon.ico", "robots.txt"}:
        return app.send_static_file(slug)

    url_id = Url.slug_to_id(slug)
    if not url_id:
        return abort(404)

    link = Url.query.get_or_404(url_id)
    app.logger.info(f"Redirecting /{slug} -> {link.href}")
    return redirect(link.href, code=301)
