"""
Common file transfer utilities
"""
try:
    import logging
    import hashlib
    from datetime import datetime
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

logger = logging.getLogger(__name__)

COMMANDS = {
            'list': ('list', 'Displays a list of all the available files'),
            'get': ('get <remote filename>', 'Downloads a file with a given filename'),
            'put': ('put <local file path> <remote file name>', 'Uploads a file with a given filename'),
}

def timestamp():
    """ Returns current time stamp. """
    return '[%s]'  % (datetime.strftime(datetime.now(), '%H:%M:%S'))

def display_message(message):
    """ Displays a message with a prepended time stamp. """
    
    logger.debug( '%s %s' % (timestamp(), message) )

def validate_file_md5_hash(file, original_hash):
    """ Returns true if file MD5 hash matches with the provided one, false otherwise. """
    return get_file_md5_hash(file) == original_hash

def get_file_md5_hash(file):
    """ Returns file MD5 hash"""
    
    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)
        
    return md5_hash.hexdigest()

def read_bytes_from_file(file, chunk_size = 8192):
    """ Read bytes from a file in chunks. """
    
    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if chunk:
                    yield chunk
            else:
                break

def clean_and_split_input(input):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """
    
    input = input.strip()
    input = input.split(' ')    
    return input

