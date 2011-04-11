from subprocess import Popen, PIPE

import clevercss


def coffee(data):
    c = Popen('coffee -p -s'.split(), stdin=PIPE, stdout=PIPE)
    return c.communicate(data)[0]


BACKENDS = {
    'clevercss': clevercss.convert,
    'coffee': coffee,
    }
