# -*- coding: utf-8 -*-
import logging
from flask import abort, Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from character_encoder import CharacterEncoder

url_shortener = CharacterEncoder()

logging.basicConfig(level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


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
    url = db.Column(db.String, unique=True, nullable=False)

    @ property
    def slug(self):
        """
        @returns shortend url string
        Note: doesn't start with / or https:// it's just the name
        """
        return url_shortener.encode(self.id)


class AppError(Exception):
    """Wrap base Exception class for app custom errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


@ app.route("/")
def root():
    return app.send_static_file('index.html')


@ app.route("/", methods=["POST"])
def index():
    try:
        url = request.form.get("url")
        if not url:
            raise AppError("Required post parameter: url missing.")

        short_url = create_link(url)
        return jsonify({"success": True, "url": url, "shortUrl": short_url})
    except AppError as e:
        return jsonify({"success": False, "message": e.message})


def create_link(url):
    """
    :param: url: string - user provided url to shorten
    @returns string - the shortened url slug
    :throws: AppError on any failure i.e. database
    """
    try:
        exists = Url.query.filter_by(url=url).first()
        if exists:
            return exists.slug

        new_link = Url(url=url)
        db.session.add(new_link)
        db.session.commit()
        return new_link.slug
    except IntegrityError as e:
        # Triggers when inserting an existing url
        raise AppError(str(e))
    except ValueError as e:
        raise AppError("A Value error occurred")
        # raise AppError("Url already exists")
    except SQLAlchemyError as e:
        # catch and rethrow exceptions with custom messages
        # TODO catch errors where url doesn't validate
        # and where
        raise AppError("SQLAlchemyError: " + str(e))


@ app.route("/<slug>")
def shortcut(slug):
    if slug in {"favicon.ico", "robots.txt"}:
        return app.send_static_file(slug)

    try:
        url_id = Url.slug_to_id(slug)
    except ValueError:
        return abort(404)

    link = Url.query.get_or_404(url_id)
    app.logger.info(f"Redirecting /{slug} -> {link.url}")
    return redirect(link.url, code=301)


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run()
