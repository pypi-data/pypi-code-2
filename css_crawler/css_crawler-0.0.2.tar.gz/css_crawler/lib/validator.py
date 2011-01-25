from nagare import validator, log
import urlparse
import string


class UrlValidator(validator.StringValidator):

    def is_url(self, msg='Not a valid url'):
        try:
            pieces = urlparse.urlsplit(self.value)
            netloc = pieces.netloc
            if ':' in netloc:
                netloc, port = netloc.rsplit(':', 1)
                assert port.isdigit()
            assert all([pieces.scheme, pieces.netloc])
            assert set(netloc) <= set(string.letters + string.digits + '-.')
            assert pieces.scheme in ['http', 'https']
            return self
        except AssertionError:
            raise ValueError(msg)
