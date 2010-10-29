# -*- coding: utf-8 -*-

"""
Helper functions which uses keyring for connection credentials saving.
"""

import keyring
from mekk.nozbe.connection import NozbeConnection
from getpass import getpass
from twisted.internet import defer

class NozbeKeyringConnection(NozbeConnection):
    """
    Keyring-integrated NozbeConnection object.
    Prompts interactively for the password, repeats the prompt
    in case of failure, saves password in the keyring and reuses it.
    """
    def __init__(self, username = None, devel = None, timeout = None):
        NozbeConnection.__init__(self, devel = devel, timeout = timeout)
        self.username = username

    @defer.inlineCallbacks
    def obtain_api_key(self, force_prompt = False):
        username = self.username
        while not username:
            username = raw_input("Your Nozbe username: ")
        keyring_password = None
        if not force_prompt:
            keyring_password = keyring.get_password(self.url, username)
            password = keyring_password
        while not password:
            password = getpass("Your (%s) Nozbe password: " % username)
        yield self.load_api_key(username, password)
        if password != keyring_password:
            keyring.set_password(self.url, username, password)
        
    # TODO: override get_request and post_request to call inherited
    # methods, catch exceptions and in case of authentication failure,
    # re-query for the password
