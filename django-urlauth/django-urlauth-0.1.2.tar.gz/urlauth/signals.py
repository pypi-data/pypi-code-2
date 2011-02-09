from django.dispatch import Signal

key_loaded = Signal(providing_args=['key', 'request'])
key_user_found = Signal(providing_args=['key', 'user', 'request'])
