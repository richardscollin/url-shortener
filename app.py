# -*- coding: utf-8 -*-
import string
from flask import Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class SlugTranslator():
    @staticmethod
    def slug_to_id(slug):
        result = 0
        mapping = string.ascii_letters
        n = len(mapping)

        for c in slug:
            if ord('a') <= ord(c) <= ord('z'):
                result += ord(c) - ord('a')
            elif ord('A') <= ord(c) <= ord('Z'):
                result += ord(c) - ord('A') + 26
            else:
                raise ValueError(f"Invalid Slug letter: {c} slug: {slug}")
            result *= n
        return result // n

    @staticmethod
    def id_to_slug(url_id):
        s = ""
        mapping = string.ascii_letters
        n = len(mapping)

        x = url_id
        while True:
            s += mapping[x % n]
            x //= n
            if x == 0:
                break

        return s

    @staticmethod
    def tests():
        for i in range(1000):
            slug = SlugTranslator.id_to_slug(i)
            reversed_i = SlugTranslator.slug_to_id(slug)
            print(i, slug, reversed_i)
            assert(i == reversed_i)


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

    @validates('url')
    def valid_url(self, key, value):
        return value.startswith("http://|https://")

    @property
    def slug(self):
        """
        @returns shortend url string
        Note: doesn't start with / or https:// it's just the name
        """
        result = SlugTranslator.id_to_slug(self.id)
        print("slug is: " + result)
        return result

    # TODO clean up these mappings are a bit messier then I intended


class AppError(Exception):
    """Wrap base Exception class for app custom errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


@app.route("/")
def root():
    return app.send_static_file('index.html')


@app.route("/", methods=["POST"])
def index():
    try:
        url = request.form.get("url")
        print(f"the url is: {url}")
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
        raise AppError(f"{e}")
    except ValueError as e:
        raise AppError("A Value error occurred")
        # raise AppError("Url already exists")
    except SQLAlchemyError as e:
        # catch and rethrow exceptions with custom messages
        # TODO catch errors where url doesn't validate
        # and where
        raise AppError("SQLAlchemyError: " + str(e))


@app.route("/<slug>")
def shortcut(slug):
    if slug in {"favicon.ico", "robots.txt"}:
        return app.send_static_file(slug)

    link = Url.query.filter_by(id=SlugTranslator.slug_to_id(slug)).first()
    if link:
        return redirect(link.url, code=301)
    else:
        return jsonify()


if __name__ == "__main__":
    db.create_all()
    app.run()
