#!/usr/bin/env python
#

import logging

import boto

log = logging.getLogger('cirrus')

class LoadBalance:
    """ Elastic Load Balancing object of cirrus
    This object takes a boto elb connection and a cirrus ec2 object and 
    has methods to perform operations on elb's.
    """

    def __init__(self, conn, base, instances):
        self.base = base
        self.conn = conn #A boto elb connection
        self.instances = instances #{instance name: instance id} of defined instances

    def create_load_balancers(self, dry_run=False):
        """Create load_balancers which don't already exist.
        It does not modify existing groups.
        """
        if self.base['load_balancers'] is None:
            return None

        balancers = {}
        for b in self.conn.get_all_load_balancers():
            balancers[b.name] = b
            
        #Check defined balancers to see if they exists
        for name, bsetup in self.base['load_balancers'].iteritems():
            log.debug('Checking load balancer ' + name)
            if name not in balancers.keys():
                log.info('Creating Load balancer ' + name)
                #create a new balancer
                listeners = [ (l['balancer_port'], l['instance_port'], l['protocol']) for l in bsetup['listeners'] ]
                if not dry_run:
                    lb = self.conn.create_load_balancer(name, bsetup['zones'], listeners)

                    #Add health check
                    lb.configure_health_check(boto.ec2.elb.HealthCheck(**bsetup['check']))

                    #add machines to the lb
                    instance_ids = [ self.instances[name] for name in bsetup['instances'] ]
                    lb.register_instances(instance_ids)
            else:
                log.info('Load balancer ' + name + ' already exists, dns name = ' + balancers[name].dns_name)
                #check that all instances are setup, extra instances are ignored
                for instance_name in bsetup['instances']:
                    instance_id = self.instances[instance_name]
                    if instance_id not in balancers[name].instances:
                        log.info('Load balancer ' + name + ' was missing instance ' + instance_name + ' adding.')
                        if not dry_run:
                            balancers[name].register_instances([instance_id, ])

    def remove_load_balancers(self, dry_run=False):
        """Remove defined load_balancers which exist.
        """
        balancers = self.conn.get_all_load_balancers()
        defined_names = [ b.name for b in self.base['load_balancers'].iterkeys() ]
        #Check defined balancers to see if they exists
        for balancer in balancers:
            if balancer.name in defined_names:
                log.info('Removing load balancer ' + balancer.name)
                if not dry_run:
                    balancer.delete()

