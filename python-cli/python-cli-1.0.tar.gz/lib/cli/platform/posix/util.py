#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
import os.path


def local_settings_file(name):
    """"Return the local settings file for `name'."""
    home = os.environ.get('HOME')
    if home is None:
        return
    fname = os.path.join(home, '.%src' % name)
    return fname
