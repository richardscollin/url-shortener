# -*- coding: utf-8 -*-
import string


class CharacterEncoder():
    def __init__(self, mapping=(string.ascii_letters + "0123456789"), min_length=2):
        if min_length < 2:
            raise ValueError

        self.mapping = mapping
        self.min_length = min_length
        self.reverse_mapping = dict([(c, i) for i, c in enumerate(mapping)])
        self.base = len(mapping)

    def decode(self, slug):
        result = 0
        for i, c in enumerate(slug[::-1]):
            result += self.reverse_mapping.get(c) * self.base ** i
        return result

    def encode(self, url_id):
        result = []

        remaining = url_id
        while remaining > 0:
            result.append(self.mapping[remaining % self.base])
            remaining //= self.base

        result.reverse()
        padding = self.mapping[0] * max(0, self.min_length - len(result))
        return padding + "".join(result)
