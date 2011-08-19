#!/usr/bin/env python
import os
import cmdln
import riak
import ConfigParser
import pprint

HOME = os.path.expanduser("~")

# Get the configuration (assume home directory, if not, default)
config = ConfigParser.RawConfigParser()

if os.path.isfile("%s/.riakc" % HOME):
    config.read("%s/.riakc" % HOME)
else:
    config.read("%s/riakc.ini" % os.getcwd())

HOST = config.get("connection", "host")
PORT = config.get("connection", "port")

PP   = pprint.PrettyPrinter(indent=4)

client = riak.RiakClient(port=int(PORT), host=HOST, transport_class=riak.RiakPbcTransport)

class RiakcException(Exception):
    pass

if not client.is_alive():
    raise RiakcException("Riak is not responding...")

class Riakc(cmdln.Cmdln):
    """
    Basic Riak command line utility.
    """
    
    name = "riakc"
    
    def do_list(self, subcmd, opts, bucket_name=None):
        """${cmd_name}: list all of the buckets in Riak
        
        If a bucket name is provided, this command will list all of
        the keys stored in the at bucket.
        
        ${cmd_usage}
        """
        
        if bucket_name:
            bucket = client.bucket(bucket_name)
            PP.pprint(bucket.get_keys())
        else:
            PP.pprint(client.get_buckets())
    
    def do_get(self, subcmd, opts, bucket_name, key):
        """${cmd_name}: get a key's data
        
        ${cmd_usage}
        """
        
        bucket = client.bucket(bucket_name)
        item   = bucket.get(key)
        
        if item._exists:
            PP.pprint(item.get_data())
        else:
            print "Key does not exist: %s" % key

    def do_get_meta(self, subcmd, opts, bucket_name, key):
        """${cmd_name}: get a key's metadata
        
        ${cmd_usage}
        """
        
        bucket = client.bucket(bucket_name)
        item   = bucket.get(key)
        
        if item._exists:
            PP.pprint(item.get_metadata())
        else:
            print "Key does not exist: %s" % key
        
    def do_delete(self, subcmd, opts, bucket_name, key):
        """${cmd_name}: delete a key
        
        ${cmd_usage}
        """
        
        bucket = client.bucket(bucket_name)
        item   = bucket.get(key)
        
        if item._exists:
            item.delete()
        else:
            print "Key does not exist: %s" % key
