# -*- coding: utf-8 -*-
import logging
import re
from flask import abort, Flask, jsonify, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import validates
from urllib.parse import urlparse
from character_encoder import CharacterEncoder

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

url_shortener = CharacterEncoder()

class Url(db.Model):
    """
    We don't store the shorted url instead we use a mapping
    from the integer id to a url that follows our shortend rules.

    This has the benefit that we can now use the database generation
    of a unique id as our way of generating the unique slug

    But this requires / assumes that the underlying database
    our id's start at 0. This seems pretty safe but we could modify
    to use a different autoincrementing int

    """
    id = db.Column(db.Integer, primary_key=True)
    href = db.Column(db.String, unique=True, nullable=False, index=True)

    @ property
    def slug(self):
        """
        @returns shortend url string
        Note: doesn't start with / or https:// it's just the name
        """
        return url_shortener.encode(self.id)

    @validates('href')
    def validate_href(self, key, href):
        """
        This function validates that the url is valid.

        It also prefixes the http:// schema to the url
        if it was not passed in by the user.
        """
        if len(href) > 2000:
            raise AppError(f"Url too long in length. Limit: 2000 characters, Length: {len(href)}.")

        split_url = urlparse(href, scheme="http")
        # urlparse will only parse valid domain names into
        # netloc. However there are several valid domain names
        # we might not want to redirect to.
        # it also does not check that the dns name is valid

        domain = split_url.netloc
        domain_with_port = split_url.netloc.rsplit(':', 2)
        if len(domain_with_port) == 2:
            (domain, _) = domain_with_port

        if split_url.netloc == '' \
            or split_url.netloc in ["localhost", "127.0.0.1"] \
            or domain in ["localhost", "127.0.0.1"]:
            raise AppError(f"Invalid url: {href}")
        
        # There are numerous other cases we could
        # validate. ipv6 etc. for now to keep simplicity
        # I will not implement that validation.
        # Worst case we attempt to redirect to an invalid
        # domain which is acceptable

        # We return the url this way because it prepends the http
        # schema if it was missing
        return split_url.geturl()

# Must be after Url def
db.create_all()

class AppError(Exception):
    """Wrap base Exception class for app custom errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


@ app.route("/", methods=["GET", "POST"])
def index():
    added = None
    urls = db.session.query(Url).order_by(Url.id.desc()).limit(10)
    # TODO handle sql error

    if request.method == "POST":
        try:
            url = request.form.get("url")
            if not url:
                raise AppError("Required post parameter: url missing.")

            added = create_link(url)

        except AppError as e:
            return render_template("index.html", error=e, urls=urls)

    return render_template("index.html", url=added, urls=urls)


def create_link(url):
    """
    :param: url: string - user provided url to shorten
    @returns string - the shortened url slug
    :throws: AppError on any failure i.e. database
    """
    try:
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
def shortcut(slug):
    if slug in {"favicon.ico", "robots.txt"}:
        return app.send_static_file(slug)

    try:
        url_id = url_shortener.decode(slug)
    except ValueError:
        return abort(404)

    link = Url.query.get_or_404(url_id)
    app.logger.info(f"Redirecting /{slug} -> {link.href}")
    return redirect(link.href, code=301)
