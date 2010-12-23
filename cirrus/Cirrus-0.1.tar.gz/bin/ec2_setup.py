#!/usr/bin/env python
#
""" ec2_setup
Run this on a yaml cloud definition an it will check the cloud to make sure your ec2 definition is setup
and if not will set it up.
"""

import logging
from optparse import OptionParser
import sys
import yaml

import boto

from cirrus.ec2 import ElasticCompute
from cirrus.elb import LoadBalance

log = logging.getLogger('cirrus')
log.addHandler(logging.StreamHandler())

def create_security_groups(conn, base, dry_run=False):
    """Create security groups which don't already exist.
    It does not modify existing groups.
    """
    groups = conn.get_all_security_groups()
    group_names = [ g.name for g in groups ]
    for name, group in base['security_groups'].iteritems():
        log.debug('Checking security group ' + name)
        if name not in group_names:
            log.info('Creating security group ' + name)
            if not dry_run:
                new_group = conn.create_security_group(name, group['description'])
                for rule in group['authorize']:
                    log.info("\tAdding rule " + str(rule))
                    if rule.has_key('src_group'):
                        rule['src_group'] = conn.get_all_security_groups([rule['src_group'], ])[0]
                    new_group.authorize(**rule)

def get_args():
    """Sets up Option parser and then resturns the parsed options and args."""
    usage = "usage: %prog [options] <yaml definition>"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--dry-run', action='store_true', dest='dry_run', default=False, \
        help="Report what would be done but do nothing.")
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=True)
    parser.add_option('-s', '--stop', action='store_true', dest='stop', default=False, \
        help="Instead of starting up defined instances stop them. Stop does not destroy EBS volumes or load balancers.")
    parser.add_option('--terminate', action='store_true', dest='terminate', default=False, \
        help="Instead of starting up defined instances terminiate them. This will also remove load balancers.")

    return parser.parse_args()

def main():
    options, args = get_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)

    #Pull from the yaml file
    def_file = open(args[0], 'r')
    definition = yaml.load_all(def_file)
    base = definition.next()

    if options.dry_run:
        log.info("Doing a dry-run, only reporting actions.")

    #Get the api connection
    conn = boto.connect_ec2(base['access_id'], base['secret_key'])

    #process security groups
    create_security_groups(conn, base, options.dry_run)

    #Run through the ec2 definitions for each type, collect instances
    instances = {}
    for defined in definition:
        ec2 = ElasticCompute(conn, base, defined)

        #process key pair
        ec2.create_key_pair(options.dry_run)

        #process instances
        if options.stop or options.terminate:
            ec2.stop_instances(options.terminate, options.dry_run)
        else:
            new_instances = ec2.create_instances(options.dry_run)
            instances.update(new_instances)

    #Process load balancing
    elb = LoadBalance(boto.connect_elb(base['access_id'], base['secret_key']), base, instances)
    if options.terminate:
        elb.remove_load_balancers(options.dry_run)
    else:
        elb.create_load_balancers(options.dry_run)

if __name__ == "__main__":
    sys.exit(main())
