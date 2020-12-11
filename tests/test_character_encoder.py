# -*- coding: utf-8 -*-
import sys
from character_encoder import CharacterEncoder
# run tests with:
# python -m pytest tests/
# from project root directory

encoder = CharacterEncoder()

emoji_encoder = CharacterEncoder(mapping="👶👧🧒👦👩", min_length=2)


def test_emoji_encoder():
    assert("👶👶" == emoji_encoder.encode(0))
    assert("👶👧" == emoji_encoder.encode(1))
    assert("👧👶" == emoji_encoder.encode(5))


def test_slug_translations_invertable():
    for i in range(1000):
        slug = encoder.encode(i)
        reversed_i = encoder.decode(slug)
        print(i, slug, reversed_i)
        assert(i == reversed_i)


def test_no_overlap():
    values = []
    for i in range(1000):
        values.append(encoder.decode(encoder.encode(i)))

    assert(len(values) == len(set(values)))


def test_special_values():
    assert(0 == encoder.decode('aa'))
    assert(61 == encoder.decode('a9'))
    assert(62 == encoder.decode('ba'))
    assert(sys.maxsize == encoder.decode(encoder.encode(sys.maxsize)))
