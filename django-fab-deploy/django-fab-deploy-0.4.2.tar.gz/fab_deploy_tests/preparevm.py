#!/usr/bin/env python
"""
Prepares VirtualBox image: takes initial snapshot for rollbacks
and configures port forwarding.
"""

import sys
from time import sleep
from fab_deploy_tests.utils import VirtualBox

def prepare_vbox(name):
    box = VirtualBox(name)
    box.modifyvm('--natpf1', 'guestssh,tcp,,2222,,22')
    box.modifyvm('--natpf1', 'http,tcp,,8888,,80')

    box.start()
    print 'Vaiting 100 seconds for OS to boot...'
    for i in range(1,11):
        sleep(10)
        print '%ds remains' % (100-i*10)

    box.snapshot('take', 'initial')
    box.stop()

if __name__ == '__main__':
    prepare_vbox(sys.argv[1])

