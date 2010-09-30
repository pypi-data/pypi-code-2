# -*- coding: utf-8 -*-
import os, sys
import setuptools
import collective.releaser

if '--name' in sys.argv:
    print os.path.basename(os.getcwd())
elif '--version' in sys.argv and '-a' not in sys.argv:
    print '0.5'
else:
    print 'Running python',  ' '.join(sys.argv)

