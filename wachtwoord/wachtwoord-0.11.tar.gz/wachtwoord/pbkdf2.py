"""Module level functions and a class for hashing and verifying passwords.

:copyright: (c) 2010 by the Guido Kollerie.
:license: BSD, see LICENSE for more details.
"""

__all__ = ['Engine', 'hash_password', 'verify_password']

import hashlib
import hmac
from wachtwoord.utils import bytes_to_base64_str, base64_str_to_bytes, random_bytes

HASHES = {'sha1': hashlib.sha1, 'sha224': hashlib.sha224,
          'sha384': hashlib.sha384, 'sha256': hashlib.sha256,
          'sha512': hashlib.sha512, 'md5': hashlib.md5}

DELIMITER = '$'

def pbkdf2_generic(b_password, b_salt, iterations, digestmod):
    """Hash a ``password`` according to the PBKDF2 specification.

    :param b_password: clear text password
    :type b_password: byte string
    :param b_salt: salt value
    :type b_salt: byte string
    :param iterations: number of times hash function should be applied
    :type iterations: integer
    :param digestmod: hash function
    :type digestmod: :mod:`hashlib` hash object or string name

    :returns: hashed password
    :rtype: byte string
    """
    b_hashed_password = b_password
    for _ in range(iterations):
        b_hashed_password = hmac.new(b_salt, b_hashed_password,
                                     digestmod).digest()
    return b_hashed_password


def hash_password(password, digestmod=hashlib.sha512, iterations=10000,
                  salt_size=32):
    """Hash a ``password`` according to the PBKDF2 specification.

    Hash a ``password `` using ``digestmod`` as the hash function, together with
    ``salt`` as the salt value for ``iterations`` number of times. This
    process of generating an hash encoded password (or derived key) is
    known as Password Based Key Derivation (Function) or PBKDF2 for short.

    See also: http://en.wikipedia.org/wiki/PBKDF2

    The main difference between this module level function and the
    :meth:`Engine.hash` method is that the verification of a valid
    :mod:`hashlib` hash object/function name and the hashing happens in one go
    for the module level function. Whereas it is split between
    :class:`Engine` instantiation (verification) and :meth:`Engine.hash`
    (hashing) for the :meth:`Engine.hash` method. The splitting is mostly useful
    for hashing many passwords using the same hash function as the
    verification only happens once.

    :param password: clear text password to be hashed
    :type password: unicode string
    :param digestmod: hash function to use
    :type digestmod: :mod:`hashlib` hash object or hash function name
    :param iterations: number of time to apply the hash function
    :type iterations: integer
    :param salt_size: length of the randomly generated salt
    :type salt_size: integer

    :returns: hash encoded string
    :rtype: unicode string
    """
    return Engine(digestmod, iterations, salt_size).hash(password)


def verify_password(password, hash_encoded_password):
    """Verify a ``password ``against an hash encoded password.

    Given a password verify it against a given hash encoded password. The hash
    encoded password needs to follow a specific format. :func:`.hash_password`
    and :meth:`Engine.hash` generate hash encoded passwords that follow this
    format.

    :param password: clear text password to be verified
    :type password: unicode string
    :param hash_encoded_password: hashed encoded password in specific format
                                  (see below)
    :type hash_encoded_password: unicode string

    :returns: True if ``password`` matches ``hash_encoded_password``, else
              False
    :rtype: boolean

    :raises ValueError: if either the ``hash_encode_password`` is incorrectly
                        formatted or if the hash function specified in the
                        ``hash_encoded_password`` is unsupported.
                        
    The hash encoded password format:

    ``digestmod$iterations$salt$hashed_password``

    * ``digestmod`` -  the hash function used to hash the password
    * ``iterations`` - the number of times the hash function is applied to
       the combination of the ``salt`` and the ``(hashed_)password``
    * ``salt`` - a random generated string to be concatenated with the
      ``password`` before applying the hash function
    * ``hashed_password`` the result of applying the hash function ``digestmod``
      ``iterations`` number of times to the concatenation of ``salt`` and
      ``(hashed_)password``.

    Both the ``salt`` and the ``hash_encoded_password`` are in base64 format.
    """
    try:
        digestmod, iterations, salt, hashed_password = hash_encoded_password.split(
            DELIMITER)
    except ValueError as e:
        raise ValueError(
            "Expected hash encoded password in format 'digestmod{0}iterations{0}salt{0}hashed_password".format(
                DELIMITER)) from e
    if digestmod not in HASHES.keys():
        raise ValueError(
            "Unsupported hash algorithm '{0}' for hash encoded password '{1}'.".format(
                digestmod,
                hash_encoded_password))
    iter = int(iterations)
    b_salt = base64_str_to_bytes(salt)
    b_hashed_password = base64_str_to_bytes(hashed_password)
    b_password = password.encode()
    return b_hashed_password == pbkdf2_generic(b_password, b_salt,
                                               iter,
                                               HASHES[digestmod])


class Engine(object):
    """Captures settings for generating password hashes according to the PBKDF2
       specification.

    See also: http://en.wikipedia.org/wiki/PBKDF2

    If multiple password hashes need to be generated instantiating a
    :class:`Engine` object that captures the shared settings is slightly more
    convenient than using the module level function :func:`.hash_password` as
    initialization and verification is done only once.
    """

    def __init__(self, digestmod=hashlib.sha512, iterations=10000,
                 salt_size=32):
        """Instantiate an Engine object that captures settings for generating
           password hashes.

        :param digestmod: hash function to use
        :type digestmod: :mod:`hashlib` hash object or function name
        :param iterations: number of times to apply the hash function
        :type iterations: integer
        :param salt_size: length of the randomly generated salt
        :type salt_size: integer

        :raises ValueError: if the ``digestmod`` is not an :mod:`hashlib` hash
                            object or hash function name.
        """
        if hasattr(digestmod, '__call__'):
            self.digestmod = digestmod
        elif digestmod in HASHES.keys():
            self.digestmod = HASHES[digestmod]
        else:
            raise ValueError(
                "Expected argument 'digestmod' to be one of the hash objects from hashlib or hashlib function name ({0}).".format(
                    ", ".join(HASHES.keys())))
        self.iterations = iterations
        self.salt_size = salt_size

    def hash(self, password):
        """Hash a ``password`` according to the PBKDF2 specification.

        Hash a ``password`` using the parameters specified in the
        :class:`Engine`` constructor.

        See also: :func:`.hash_password`

        :param password: clear text password to be hashed
        :type password: unicode string

        :returns: hash encoded string
        :rtype: unicode string
        """
        b_salt = random_bytes(self.salt_size)
        b_password = password.encode()
        b_hashed_password = pbkdf2_generic(b_password, b_salt, self.iterations,
                                           self.digestmod)
        digestmod = self.digestmod.__name__.replace('openssl_', '')
        return digestmod + DELIMITER + str(
            self.iterations) + DELIMITER + bytes_to_base64_str(
            b_salt) + DELIMITER + bytes_to_base64_str(b_hashed_password)

    def verify(self, password, hash_encoded_password):
        """Verify a password against an hash encoded password.

        See also: :func:`.verify_password`
        """
        return verify_password(password, hash_encoded_password)
