from . import pubkey
from . import ldapchecker


def get(name):
    if name == 'ldap':
        return ldapchecker.get_checker()
    elif name == 'pubkey':
        return pubkey.GratePublicKeyChecker()
