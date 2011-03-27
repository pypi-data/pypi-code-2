#!/usr/bin/env python

from . import copy_to_clipboard, generate_password

import getpass

def main():
    copy_to_clipboard(generate_password(getpass.getpass('Password: '), raw_input('Token: ')))

