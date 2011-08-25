#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import sys

if sys.platform in ('linux2',):
    from cli.platform.posix.terminal import PosixTerminal as Terminal
    from cli.platform.posix.util import *

elif sys.platform in ('win32',):
    pass
