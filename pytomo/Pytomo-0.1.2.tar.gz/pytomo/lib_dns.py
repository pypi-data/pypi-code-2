#!/usr/bin/env python
"""Module to retrieve the IP address of a URL out of a set of nameservers
"""

from urlparse import urlsplit
import sys

import pytomo.dns.resolver as dns_resolver
import pytomo.dns.exception as dns_exception

import pytomo.config_pytomo as config_pytomo

def get_default_name_servers():
    "Return a list of IP addresses of default name servers"
    default_resolver = dns_resolver.get_default_resolver()
    # find out the exception to catch in case of error
    return default_resolver.nameservers[0]

def get_ip_addresses(url):
    "Return a list of tuples with the IP address and the resolver used"
    if not url.startswith('http://'):
        url = 'http://'.join(('', url))
    hostname = urlsplit(url).netloc
    results = []
    # Set the DNS Server
    resolver = dns_resolver.Resolver()
    default_resolver = ('default', get_default_name_servers())
    dns_servers = [default_resolver] + config_pytomo.EXTRA_NAME_SERVERS
    for (name, server) in dns_servers:
        config_pytomo.LOG.debug("DNS resolution using %s on this address %s"
                                % (name, server))
        resolver.nameservers = [server]
        try:
            rdatas = resolver.query(hostname)
        except dns_resolver.Timeout:
            config_pytomo.LOG.info("DNS timeout for %s" % name)
            rdatas = None
            continue
        except dns_exception.DNSException, mes:
            config_pytomo.LOG.exception('Uncaught DNS Exception: %s' % mes)
            rdatas = None
            continue
        if rdatas:
            config_pytomo.LOG.debug("URL %s resolved as: %s"
                                    % (hostname, rdatas[0].address))
            results.append((rdatas[0].address, '_'.join((name, server))))
    return results

if __name__ == '__main__':
    import logging
    config_pytomo.LOG = logging.getLogger()
    config_pytomo.LOG.setLevel(config_pytomo.LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)d - "
                                      "%(levelname)s - %(message)s")
    handler.setFormatter(log_formatter)
    config_pytomo.LOG.addHandler(handler)
    get_ip_addresses(sys.argv[1])

