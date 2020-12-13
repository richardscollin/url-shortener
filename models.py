from sqlalchemy.orm import validates
from urllib.parse import urlparse
from app import db, AppError
from character_encoder import CharacterEncoder

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

    Actually sqlite starts indexing at 1. This isnt's a problem though.
    Our starting shortened url is then '/ab'

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

    @staticmethod
    def slug_to_id(user_slug):
        try:
            return url_shortener.decode(user_slug)
        except ValueError:
            return None

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
