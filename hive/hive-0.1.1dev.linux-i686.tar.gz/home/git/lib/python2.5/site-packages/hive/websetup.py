"""Setup the hive application"""
import logging

import pylons.test

from hive.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup hive here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    # Setup for gitolite-admin
    # 1. Add repo host ssh configuration to ~/.ssh/config
    # 1. Pull gitolite-admin repository to local disk
    # 2. Generate ssh-rsa public key and append it into ~/.ssh/authorized_keys
    # 3. 
