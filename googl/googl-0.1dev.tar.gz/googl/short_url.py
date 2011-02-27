from json import loads

class ShortUrl(object):

    def __init__(self, response):
        self.response_dict = loads(response)

    def __getitem__(self, item):
        return self.response_dict[item]

    def __repr__(self):
        return self.response_dict.__repr__()

    def get(self, key):
        return self.response_dict.get(key)

