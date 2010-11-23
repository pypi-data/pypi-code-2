''' Copyright 2009 Peter Sanchez <petersanchez@gmail.com>.  
    See BSD-LICENSE for license information.
'''

# First, require the Zerigo DNS module.

import zerigodns

# import other modules to help with the 
# examples below. They are not required.
import time

# All API request require a Zerigo account and an Account API key. We'll set
# them here for later reference. The api_user is your regular login email.
# The api_key comes from the Preferences page
# (Manage Account . NS . Preferences).

api_user = 'test@example.com'

api_key  = 'ca01ffae311a7854ea366b05cd02bd50'

myzone = zerigodns.NSZone(api_user, api_key)

# Note: This example assumes that there is at least one domain/zone already
#       existing for the above referenced account.

# We'll start by retrieving a list of domains for this account. Note that the
# API refers to domains as zones. Note that API attributes are addressed like
# object variables: zone.domain
# All attributes will have underscores in the name instead of dashes.
# eg: zone.default_ttl, not zone.default-ttl

print "\nRetrieving list of first 20 zones...\n"
zones = myzone.find_all({'per_page': 20, 'page': 1})

# Now print a list of those zones
for zone in zones:
  print "  %s (id:%i)\n" % (zone.domain, zone.id)

# And show exactly how many results there were. Note that update_count() is
# attached to each zone object, so we just pick the first one here.
if zones:
  disp = len(zones)
  print "  (1-%i of %i displayed)\n" % (disp, myzone.count)
else:
  print "  (0 of 0 displayed)\n"


# We'll list all hosts for the first zone from the last request.

zone = zones[0]
print "\nHosts for zone %s (id:%i)\n" % (zone.domain, zone.id)

# By default the zone listings do not include hosts.
# Reload the zone to get hosts

zone.reload()
for host in zone.hosts:
  print "  %s (id:%i)\n" % (host.hostname, host.id)

# While not demonstrated here, hosts[0].update_count() works just like 
# zones.


# Now we'll load a single zone. In this case, it's the first zone returned in
# the last request.

print "\nLoading a single zone...\n"
zone = myzone.find(zones[0].id)

print "  Loaded zone #%i (%s)\n" % (zone.id, zone.domain)


# Now we'll load the single zone again, but using the domain instead of the
# zone's id.

print "\nLoading a single zone by domain name...\n"
zone = myzone.find_by_domain(zones[0].domain)

print "  Loaded zone #%i (%s)\n" % (zone.id, zone.domain)


# Now we'll try to load a non-existent zone and catch the error.

print "\nLoading a non-existent zone...\n"
try:
  zone2 = myzone.find(987654321)
  print "  Loaded zone #%i (%s)\n" % (zone2.id, zone2.domain)
except zerigodns.ZerigoNotFound:
  print "  Zone not found\n"


# Let's create a random zone.

print "\nCreating a random zone...\n"

now = str(time.time())[:5]
vals = {
    'domain': "example-%s.org" % now, 
    'ns_type': 'pri_sec', # options for this are 'pri_sec' (the default and most common), 'pri', and 'sec' -- see the API docs for details
}

newzone = myzone.create(vals)
# Use the has_errors() method to check for errors:
if newzone.has_errors():
  print "  There was an error saving the new zone.\n"
  for err in newzone.errors:
    print "    ", err
else:
  print "  Zone %s created successfully with id #%i.\n" (newzone.domain, newzone.id)


# Then we'll update that same zone.

print "\nNow adding NS1 and changing to 'sec'...\n"

newzone.ns_type = 'sec'
# This would almost always be a domain other than the one for the zone we're 
#   editing, but we'll use this anyway. 
newzone.ns2 = "master.example-%s.org" % now 
if newzone.save():
  print "  Changes saved successfully.\n"
else:
  print "  There was an error saving the changes.\n"
  for err in newzone.errors:
    print "    ", err


# And we'll update it again.

print "\nNow setting slave_nameservers and changing to 'pri'...\n"

newzone.ns_type = 'pri'
newzone.slave_nameservers = "ns8.example-%s.org,ns9.example-%s.org" % (now, now)
if newzone.save():
  print "  Changes saved successfully.\n"
else:
  print "  There was an error saving the changes.\n"
  for err in newzone.errors:
    print "    ", err


# Add a host to the zone.

print "\nAdding a host to the zone.\n"

vals2 = {
    'hostname': 'www',
    'host_type': 'A',
    'data': '10.10.10.10',
    'ttl': 86400,
}

# A host has to be assigned to a zone. That can be done by including 'zone_id'
# in the vals2 array or by passing the id or an NSZone object as the second
# parameter to create().
newhost = newzone.create_host(vals2)
if newhost.has_errors():
  print "  There was an error saving the new host.\n"
  for err in newhost.errors:
    print "    ", err
else:
  print "  Host %s created successfully with id #%i.\n" % (newhost.hostname, newhost.id)


# To make the new host show up in the zone, either the zone needs to be 
# reloaded or just the hosts can be reloaded. We'll also reload the host
# just for fun.

print "\nReloading the host...\n"

newhost.reload()

print "\nReloading the zone...\n"

newzone.reload()


# Update the host.

print "\nChanging the host ttl to use the zone's default...\n"

host = newzone.hosts[0]
host.ttl = null
if host.save():
  print "  Changes saved successfully.\n"
else:
  print "  There was an error saving the changes.\n"
  for err in host.errors:
    print "    ", err


# Delete the host.

print "\nDeleting this host...\n"

if newhost.destroy():
  print "  Successful.\n"
else:
  print "  Failed.\n"


# Now delete this zone.

print "\nDeleting the zone...\n"

if newzone.destroy():
  print "  Successful.\n"
else:
  print "  Failed.\n"
