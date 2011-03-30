#!/usr/bin/env python

"""Module to generate the RTT times of a ping

 Sample for windows:

        ['\n', 'Pinging 173.194.24.138 with 32 bytes of data:\n',
        'Reply from 173.194.24.138: bytes=32 time=149ms TTL=43\n',
        'Reply from 173.194.24.138: bytes=32 time=149ms TTL=43\n',
        'Reply from 173.194.24.138: bytes=32 time=148ms TTL=43\n',
        'Reply from 173.194.24.138: bytes=32 time=149ms TTL=43\n',
        'Reply from 173.194.24.138: bytes=32 time=148ms TTL=43\n',
        '\n', 'Ping statistics for 173.194.24.138:\n', '
        Packets: Sent = 5, Received = 5, Lost = 0 (0% loss),\n',
        'Approximate round trip times in milli-seconds:\n', '
        Minimum = 148ms, Maximum = 149ms, Average = 148ms\n']

"""

from __future__ import with_statement
import os
import re

import pytomo.config_pytomo as config_pytomo

RTT_MATCH_LINUX = r"rtt min/avg/max/mdev = "
RTT_PATTERN_LINUX = r"(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/\d+.\d+ ms"
PING_OPTION_LINUX = '-c'

RTT_MATCH_WINDOWS = r"Minimum = "
RTT_PATTERN_WINDOWS = (
    r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms")
PING_OPTION_WINDOWS = '-n'

RTT_MATCH_DARWIN = "round-trip min/avg/max/stddev = "
RTT_PATTERN_DARWIN = RTT_PATTERN_LINUX
PING_OPTION_DARWIN = PING_OPTION_LINUX

def configure_ping_options(ping_packets=config_pytomo.PING_PACKETS):
    "Store in config_pytomo module the config for RTT matching"
    if config_pytomo.SYSTEM.lower().startswith('linux'):
        config_pytomo.ping_option_nb_pkts = ' '.join((PING_OPTION_LINUX,
                                                      str(ping_packets)))
        config_pytomo.rtt_match = RTT_MATCH_LINUX
        config_pytomo.rtt_pattern = ''.join((RTT_MATCH_LINUX,
                                             RTT_PATTERN_LINUX))
    elif (config_pytomo.SYSTEM.lower().startswith('microsoft')
          or config_pytomo.SYSTEM.lower().startswith('windows')):
        config_pytomo.ping_option_nb_pkts = ' '.join((PING_OPTION_WINDOWS,
                                                      str(ping_packets)))
        config_pytomo.rtt_match = RTT_MATCH_WINDOWS
        config_pytomo.rtt_pattern = ''.join((RTT_MATCH_WINDOWS,
                                             RTT_PATTERN_WINDOWS))
    elif config_pytomo.SYSTEM.lower().startswith('darwin'):
        config_pytomo.ping_option_nb_pkts = ' '.join((PING_OPTION_DARWIN,
                                                      str(ping_packets)))
        config_pytomo.rtt_match = RTT_MATCH_DARWIN
        config_pytomo.rtt_pattern = ''.join((RTT_MATCH_DARWIN,
                                             RTT_PATTERN_DARWIN))
    else:
        config_pytomo.LOG.warn("Ping option is not known on your system: %s"
                               % config_pytomo.SYSTEM)
        return None
    config_pytomo.RTT = True

def ping_ip(ip_address, ping_packets=config_pytomo.PING_PACKETS):
    "Return a list of the min, avg, max and mdev ping values"
    if not config_pytomo.RTT:
        configure_ping_options(ping_packets)
        if not config_pytomo.RTT:
            config_pytomo.LOG.warn("Not able to process ping on your system")
            return None
    my_cmd = 'ping %s %s' % (config_pytomo.ping_option_nb_pkts, ip_address)
    ping_result = os.popen(my_cmd)
    rtt_stats = None
    # instead of grep which is less portable
    for rtt_line in ping_result:
        if config_pytomo.rtt_match in rtt_line:
            rtt_stats = rtt_line.strip()
            break
    if not rtt_stats:
        config_pytomo.LOG.info("No RTT stats found")
        return None
    rtt_times = re.search(config_pytomo.rtt_pattern, rtt_stats)
    if rtt_times:
        rtt_values = rtt_times.groups()
        config_pytomo.LOG.debug(
            "RTT stats found for ip: %s" % ip_address)
        return map(float, rtt_values)
    config_pytomo.LOG.error(
        "The ping returned an unexpected RTT fomat: %s" % rtt_times)
    return None

