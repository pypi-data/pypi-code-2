import hmac
import hashlib
import binascii
import urlparse
import urllib


class Parameters(object):
    def __init__(self, sources, skip=None):
        self.sources = sources
        self.skip = set(skip or [])

    @property
    def composed(self):
        """ Composes multiple parameter sources in a single object. In case
            multiple sources have the same parameter name the values are
            appended in a list.
            The first occurence of a key that is present in the skipset
            will be skipped.
        """
        skipset = self.skip.copy()
        composed_parameters = dict()
        for source in self.sources:
            for parameter_name, parameter_value in source.items():
                if parameter_name in skipset:
                    skipset.remove(parameter_name)
                    continue
                value_list = composed_parameters.setdefault(parameter_name, [])
                if isinstance(parameter_value, list):
                    value_list.extend(parameter_value)
                else:
                    value_list.append(parameter_value)
        return composed_parameters

    def __iter__(self):
        return self.unpack()

    def unpack(self):
        """ Iterating through this objects will yield sorted (key, value)
            tuples. In case multiple values are present for a key, for each
            value a tuple will be generated.
        """
        composed = self.composed
        for parameter_name in sorted(composed.keys()):
            parameter_values = composed[parameter_name]
            for parameter_value in sorted(parameter_values):
                yield parameter_name, parameter_value

    def coerce(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        return value.encode('utf-8')

    @property
    def normalized(self):
        return '&'.join('%s=%s' % (self.coerce(parameter_name),
                                   self.coerce(parameter_value))
                        for parameter_name, parameter_value in self)


class Url(object):
    def __init__(self, url):
        self.url = url

    @property
    def normalized(self):
        """ Ignore the parts of the url that aren't interesting here. """
        encoded_url = self.url.encode('utf-8')
        scheme, netloc, path, _, _, _ = urlparse.urlparse(encoded_url)
        return urlparse.urlunparse((scheme, netloc, path, None, None, None))


def add_methods(cls):
    for method in cls.METHODS:
        setattr(cls, method.lower(), method.upper())
    return cls

@add_methods
class Method(object):
    METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']


class SignatureBaseString(object):
    def __init__(self, method, normalized_url, normalized_parameters):
        self.method = method
        self.normalized_url = normalized_url
        self.normalized_parameters = normalized_parameters

    def combine_components(self):
        """ Combines the pieces used in the signatune base string. """
        return '&'.join([self.encode(self.method),
                         self.encode(self.normalized_url),
                         self.encode(self.normalized_parameters)])

    def encode(self, component):
        """ Encodes the components of the signature base string. """
        return urllib.quote(component, safe='~') # _.- are quoted by default

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.combine_components())


class Signature(object):
    def __init__(self, text_to_sign, secret):
        self.text_to_sign = text_to_sign
        self.secret = secret

    def generate(self):
        """ Default (OAuth compatible) signature method implementation. """
        hash = hmac.HMAC(secret, text_to_sign, hashlib.sha1).digest()
        return binascii.b2a_base64(hash)[:-1]

    def __eq__(self, right_signature):
        """ Compares the signatures in a way that is safe against
            timing attacks.
        """
        left_signature = self.generate()
        right_signature = right_signature.generate()
        equals = len(left_signature) == len(right_signature)
        if equals:
            for left_letter, right_letter in zip(left_signature,
                                                 right_signature):
                if not (left_letter == right_letter):
                    equals = False
        return equals

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.generate())
