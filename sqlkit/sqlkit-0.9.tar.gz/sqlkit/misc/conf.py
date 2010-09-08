import os
from ConfigParser import ConfigParser, NoSectionError

class MissingNickDefinition(Exception): pass
class Opts(object): pass


def read_conf(nick, opts=None):
    """
    read sqledit configurations for 'nick' and return an opts object
    with values in configuration possibly overwritten by values in opts.
    opts can be an optionparse.Values object or a dict.
    :param nick: the nickname for which we want the configuration
    :param opts: the optparse.Values object or a dict
    """
    from copy import deepcopy

    if opts is None:
        opts = Opts()
        
    dbconf = os.path.join(os.getenv('HOME'), '.sqledit', 'nicks')
    lopts = deepcopy(opts)

    def loop_on_opts(c, opts, nick=nick):
        """
        implements "copy" option in .sqleditdb
        """

        for key, val in c.items(nick):
            if key == 'copy':
                loop_on_opts(c, opts, nick=val)
        
        for key, val in c.items(nick):
            if key == 'copy':
                continue
            if getattr(lopts, key, None) is None:
                setattr(opts, key, val)
        

    if os.path.exists(dbconf):
        c = ConfigParser()
        c.read(dbconf)
        loop_on_opts(c, opts, nick)
        return opts
    else:
        raise MissingNickDefinition

