"""\
Permissions related to a user's username
"""

def is_valid_user(marble):
    if not marble.bag.http.environ.get('REMOTE_USER'):
        return 'not_authenticated'
    return True

