#!/usr/bin/env python
#

import logging
import time

#Filter out the pycrypto(used by paramiko) deprecation warnings. See https://bugs.launchpad.net/paramiko/+bug/271791
import warnings
from Crypto.pct_warnings import RandomPool_DeprecationWarning
warnings.filterwarnings('ignore', category=RandomPool_DeprecationWarning)
import paramiko

log = logging.getLogger('cirrus')

class ElasticCompute:
    """ Elastic Compute Cloud object of cirrus
    This object takes a boto ec2 connection and ec2 definitions and provides
    methods to perform operations on ec2 infrastructure.
    """
    
    def __init__(self, conn, base, defined_nodes):
        self.conn = conn #Boto EC2 connection
        self.base = base
        self.nodes = defined_nodes

    def create_instance(self, node_name):
        """Creates a new instance based on the node definition. Returns the instance."""
        image = self.conn.get_image(self.nodes['image'])
        reservation = image.run(key_name=self.nodes['key']['name'], 
        security_groups=self.nodes['security_groups'], instance_type=self.nodes['type'], \
            monitoring_enabled=self.nodes['monitoring'])
        log.debug('reservation ' + str(reservation))
        inst = reservation.instances[0]
        log.debug('inst ' + inst.id)

        #Make sure it starts before doing anything else
        while inst.state != 'running':
            log.debug('Waiting for instance to start up, current state ' + inst.state)
            time.sleep(5)
            inst.update()

        #Assign the name
        self.conn.create_tags([inst.id], {'Name':node_name})

        #Run bootstrap commands
        if self.nodes.has_key('deploy_cmds'):
            #Sleep for a minute before trying this
            time.sleep(60)
            for cmd in self.nodes['deploy_cmds']:
                self.ssh_cmd(cmd, self.nodes['key']['user'], 
                inst.public_dns_name, self.nodes['key']['file'])

        return inst

    def create_instances(self, dry_run=False):
        """Create defined instances that don't exist.
        If dry_run is set just log the action but don't perform it.
        """
        instances = {}
        names = self.get_instance_names()
        for name in self.nodes['names']:
            if name not in names:
                log.info('Starting ' + name)
                if not dry_run:
                    instances[name] = self.create_instance(name).id
            else:
                inst = self.get_instance(name)
                instances[name] = inst.id
                if inst.state != 'running' and inst.state != 'pending':
                    if not dry_run:
                        inst.start()
                    if inst.public_dns_name is not None:
                        log.info('Instance ' + name + " exists but isn't running, starting.\n\tPublic dns:" \
                            + inst.public_dns_name)
                    else:
                        log.info('Instance ' + name + " exists but isn't running, starting. Name not yet known.")
                else:
                    log.info('Instance ' + name + ' exists and has public dns name: ' + inst.public_dns_name)

        return instances

    def create_key_pair(self, dry_run=False):
        """Creates a key pair if it doesn't already exist.
        Returns the key object."""
        key_name = self.nodes['key']['name']
        key_file = self.nodes['key']['file']
        key = self.conn.get_key_pair(key_name)
        if key is None:
            log.info('Creating key pair ' + key_name)
            if not dry_run:
                key = conn.create_key_pair(key_name)
                if os.path.exists(key_file):
                    log.error('Key file ' + key_file + " already exists!/nNot saving newly create key " + key_name)
                else:
                    key.save(key_file)

        return key

    def get_instance(self, name):
        """Given a name find the instance.
        I assume names are unique for instances."""
        return self.conn.get_all_instances(filters={'tag:Name':name})[0].instances[0]

    def get_instance_names(self):
        """Return a list of named instances."""
        instances = []
        for r in self.conn.get_all_instances():
            instances.extend(r.instances) 
        #The above code finds all instances, below only the named ones
        tags = self.conn.get_all_tags(filters={'key':'Name'})
        names = []
        for tag in tags:
            if tag.res_id[0] == 'i': #only instances not anything else with a tag
                names.append(tag.value)
        log.debug('Found names ' + str(names))
        if len(instances) != len(names):
            log.warning("There are %d instances running, %d are named" % (len(instances), len(names)) + \
            "\nThis script only deals with named instances.")
        return names

    @staticmethod
    def ssh_cmd(cmd, user, host, key_file):
        """Run the ssh command on the given host, logging in with the specified key."""
        log.debug('Running command %s on %s as %s' % (cmd, host, user))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=host, username=user, pkey=paramiko.RSAKey(filename=key_file))
            stdin, stdout, stderr = ssh.exec_command(cmd)
        except Exception, msg:
            log.error("ssh command %s caused a python exception:\n%s" % (cmd, str(msg)))
        else:
            out = stdout.read()
            err = stderr.read()
            if len(err) > 0:
                log.error("Command %s exited with stdout:\n%s\nstderr:\n%s" % (cmd, out, err))

    def stop_instances(self, terminate=False, dry_run=False):
        """Stop defined instances that exist.
        If dry_run is set just log the action but don't perform it.
        If terminate is defined the nodes are terminated not stopped.
        """
        names = self.get_instance_names()
        for name in self.nodes['names']:
            if name in names:
                if not dry_run:
                    inst = self.get_instance(name)
                    if inst.state != 'stopped':
                        if terminate:
                            log.info('Terminating ' + name)
                            inst.terminate()
                        else:
                            log.info('Stopping ' + name)
                            inst.stop()
