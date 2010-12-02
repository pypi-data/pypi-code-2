import os
from zc.buildout import UserError
from zc.buildout.buildout import MissingOption

prefix_radix = {
    "0b": 2,
    "0o": 8,
    "0x": 16,
    }

def load(buildout):
    try:
        new_mask = buildout['buildout']['umask']
        if new_mask[0] == '0' and new_mask[1].isdigit():
            radix = 8
        else:
            radix = prefix_radix.get(new_mask[:2].lower(), 10)
        new_mask = int(new_mask, radix)
        buildout.__old_mask = os.umask(new_mask)
    except KeyError:
        # TODO: Print warning.
        raise MissingOption("Missing umask option.")
    except ValueError:
        raise UserError("Invalid value for umask: %s" % (new_mask))
