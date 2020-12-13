import re
from sqlalchemy.orm import validates
from urllib.parse import urlparse
from app import app, db, AppError
from character_encoder import CharacterEncoder

if app.config['EMOJI']:
    with open("emojis.txt") as f:
        emoji_data = f.read()
        emoji_data = emoji_data.replace(" ", "").replace("\n", "")
    url_shortener = CharacterEncoder(mapping=emoji_data)
else:
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
        
        split_url = urlparse(href)

        # this blog post describes in detail the following regex
        # https://medium.com/@vaghasiyaharryk/9ab484a1b430
        # Summary of rules:
        # Valid url cannot start or end with -
        # The valid chars are in range [A-Za-z0-9-]
        # and there must be between 1 and 63 characters
        # finally restrict the tld to between 2 and 6 chars
        if not re.match(r"^((?!-)[A-Za-z0–9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$", split_url.netloc):
            raise AppError(f"Invalid url: {href}")
        
        # For now I've decided to reject raw IPv4 and IPv6 addresses, and localhost

        return href
