from django.conf import settings

NETCASH_TARGET_URL = 'https://gateway.netcash.co.za/vvonline/ccnetcash.asp'

NETCASH_USERNAME = settings.NETCASH_USERNAME
NETCASH_PASSWORD = settings.NETCASH_PASSWORD
NETCASH_PIN = settings.NETCASH_PIN
NETCASH_TERMINAL_NUMBER = settings.NETCASH_TERMINAL_NUMBER

# request.META key with client ip address
NETCASH_IP_HEADER = getattr(settings, 'NETCASH_IP_HEADER', 'REMOTE_ADDR')

# NETCASH_TEST_MODE = getattr(settings, 'NETCASH_TEST_MODE', False)
