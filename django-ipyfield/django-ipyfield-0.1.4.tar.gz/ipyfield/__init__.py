__version__ = '0.1.4'

import IPy


class IP(IPy.IP):
    """
    Wrap IPy.IP to prevent AttributeError getting raised while comparing IP
    instances to non-IP instances.
    """
    def __cmp__(self, other):
        if not isinstance(other, IPy.IPint):
            return -2
        return super(IP, self).__cmp__(other)

