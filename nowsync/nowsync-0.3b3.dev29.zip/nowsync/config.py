from __future__ import with_statement
import os

import yaml

def load_config():
    path = None
    if os.path.exists('nowsync.yaml'):
        path = 'nowsync.yaml'
    if 'NOWSYNC_SETTINGS' in os.environ:
        path = os.environ['NOWSYNC_SETTINGS']
    if path is None:
        raise Exception('Could not find nowsync.yaml in current folder, '
                        'NOWSYNC_SETTINGS is not set, too.')
    with open(path, 'rt') as file:
        config = yaml.load(file)
    return config