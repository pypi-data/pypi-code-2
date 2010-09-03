from hashlib import md5

CONTROL_CHARACTERS = set([chr(i) for i in range(0,33)])
CONTROL_CHARACTERS.add(chr(127))

def sanitize_memcached_key(key, max_length=250):
    """ Removes control characters and ensures that key will
        not hit the memcached key length limit by replacing
        the key tail with md5 hash if key is too long.
    """
    key = ''.join([c for c in key if c not in CONTROL_CHARACTERS])
    if len(key) > max_length:
        hash = md5(key).hexdigest()
        key = key[:max_length-33]+'-'+hash
    return key

def get_args_string(args, kwargs):
    key = ""
    if args:
        key += unicode(args)
    if kwargs:
        key += unicode(kwargs)
    return key


