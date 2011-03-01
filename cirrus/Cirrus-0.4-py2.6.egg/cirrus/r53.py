#!/usr/bin/env python
#

import logging
import tempfile

import dns
import dns.zone

log = logging.getLogger('cirrus')

class Zone:
    """ An interface to Amazon web services route 53.
    The class defines an aws zone and can create the resource records,
    or it can compare the existing Resource Records to a bind style zone file and update.
    The resource records must be sent to amazon as a xml file, the format can be found at.
    http://docs.amazonwebservices.com/Route53/latest/APIReference/index.html?API_ChangeResourceRecordSets.html
    """

    def __init__(self, conn, zone_name):
        self.conn = conn
        self.zone_name = zone_name
        #Set on create or exists call
        self.id = None
        self.xml_header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + \
            "<ChangeResourceRecordSetsRequest xmlns=\"https://route53.amazonaws.com/doc/2010-10-01/\">\n" + \
            " <ChangeBatch>\n" + "  <Comment>Updates to Zone " + self.zone_name + "</Comment>\n" + "  <Changes>\n"
        self.xml_footer = "  </Changes>\n" + " </ChangeBatch>\n" + "</ChangeResourceRecordSetsRequest>\n"

    def __repr__(self):
        """Return a bind style zone file for the current zone in aws."""
        if not self.exists():
            return self.zone_name + " does not exist."

        dnszone = self._to_dnszone()
        tmp = tempfile.TemporaryFile()
        dnszone.to_file(tmp)
        tmp.seek(0)
        return "Zone " + self.zone_name + "\n" + tmp.read()

    def _change_xml(self, action, name, rtype, ttl, values):
        """Returns amazon Change xml for an action on an entry."""
        xmlout = "   <Change>\n" + "    <Action>" + action + "</Action>\n" + "     <ResourceRecordSet>\n" + \
            "      <Name>" + name + "</Name>\n" + "      <Type>" + rtype + "</Type>\n" + \
            "      <TTL>" + str(ttl) + "</TTL>\n" + "      <ResourceRecords>\n"

        for rvalue in values:
            xmlout += "       <ResourceRecord>\n" + "        <Value>" + rvalue + "</Value>\n" + \
            "       </ResourceRecord>\n" 
            
        xmlout += "     </ResourceRecords>\n" + "    </ResourceRecordSet>\n" + "   </Change>\n"
        return xmlout

    def _add_change_xml(self, name, rtype, ttl, values):
        """Returns amazon Change xml for adding an entry."""
        return self._change_xml('CREATE', name, rtype, ttl, values)

    def _delete_change_xml(self, name, rtype, ttl, values):
        """Returns amazon Change xml for deleting an entry."""
        return self._change_xml('DELETE', name, rtype, ttl, values)

    def _update_change_xml(self, name, rtype, ttl, old_values, new_values):
        """Returns amazon Change xml for updating an entry."""
        xmlout = self._change_xml('DELETE', name, rtype, ttl, old_values)
        xmlout += self._change_xml('CREATE', name, rtype, ttl, new_values)
        return xmlout

    def _create_changeset(self, adds, deletes, updates):
        """Create amazon changeset xml for adds and deletes and updates to a zone.
        Return a list of individual changesets.
        """
        if len(adds) == 0 and len(deletes) == 0 and len(updates) == 0:
            return None

        changesets = []

        #Splitting my rrecords should be moved to a method it is nearly identical each time I do it.
        rrecord_keys = deletes.keys()
        rrecord_groups = [ rrecord_keys[n:n+100] for n in range(0, len(rrecord_keys), 100)]
        for rrecords_slice in rrecord_groups: 
            xmlout = self.xml_header
            for key in rrecords_slice:
                xmlout += self._delete_change_xml(key[0], key[1], key[2], deletes[key])
            xmlout += self.xml_footer
            changesets.append(xmlout)

        rrecord_keys = updates.keys()
        rrecord_groups = [ rrecord_keys[n:n+50] for n in range(0, len(rrecord_keys), 50)]
        for rrecords_slice in rrecord_groups: 
            xmlout = self.xml_header
            for key in rrecords_slice:
                xmlout += self._update_change_xml(key[0], key[1], key[2], updates[key][0], updates[key][1])
            xmlout += self.xml_footer
            changesets.append(xmlout)

        rrecord_keys = adds.keys()
        rrecord_groups = [ rrecord_keys[n:n+100] for n in range(0, len(rrecord_keys), 100)]
        for rrecords_slice in rrecord_groups: 
            xmlout = self.xml_header
            for key in rrecords_slice:
                xmlout += self._add_change_xml(key[0], key[1], key[2], adds[key])
            xmlout += self.xml_footer
            changesets.append(xmlout)

        return changesets

    def _compare(self, from_zone, to_zone):
        """Compare two dns zones and return resource record dictionaries for add deletes and updates.
        Ignores SOA and root NS records because Amazon autogenerates those."""
        from_records = self._get_rrecords(from_zone)
        to_records = self._get_rrecords(to_zone)
        adds = {}
        deletes = {}
        updates = {}

        for key in to_records.iterkeys(): #key is [name, rtype, ttl]
            name = key[0]
            rtype = key[1]
            #skip records amazon automatically generates
            if rtype == 'NS' and name[:-1] == self.zone_name:
                continue
            elif rtype == 'SOA':
                continue
            if from_records.has_key(key):
                from_records[key].sort() #I sort both to avoid ordering issues
                to_records[key].sort()
                if from_records[key] != to_records[key]:
                    log.debug("Updating %s %s %s to %s" % (key[0], key[1], key[2], to_records[key]))
                    updates[key] = [from_records[key], to_records[key]]
                del from_records[key] #no-op or modify either way pull from from_records.
            else:
                adds[key] = to_records[key]
                log.debug("Adding %s %s %s %s" % (key[0], key[1], key[2], to_records[key]))

        #Anything remaining in the from_records is a delete
        for key in from_records.iterkeys():
            deletes[key] = from_records[key]
            log.debug("Removing %s %s %s %s" % (key[0], key[1], key[2], from_records[key]))

        return adds, deletes, updates

    def _create_xml(self, zone_file):
        """Create a list of Amazon change resource record xml given a bind style zone file.
        There is one xml string in the list for each 100 entries."""
        dnszone = dns.zone.from_file(zone_file, origin=self.zone_name, relativize=False)
        rrecords = self._get_rrecords(dnszone)

        xmllist = []
        rrecord_keys = rrecords.keys()
        rrecord_groups = [ rrecord_keys[n:n+100] for n in range(0, len(rrecord_keys), 100)]
        for rrecords_slice in rrecord_groups: 
            xmlout = self.xml_header

            for key in rrecords_slice:
                xmlout += self._add_change_xml(key[0], key[1], key[2], rrecords[key])

            xmlout += self.xml_footer
            xmllist.append(xmlout)

        return xmllist
    
    def _get_rrecords(self, dnszone):
        """Given a dns zone return a dictionary of rrecords, with a format
        {(name, rtype, ttl): rvalue} where each variable is a string.
        Skips any SOA entries and NS entries for the root.
        """
        rrecords = {}
        for name, ttl, rdata in dnszone.iterate_rdatas():
            rtype = dns.rdatatype.to_text(rdata.rdtype)
            name = str(name)
            if rtype == 'NS' and name[:-1] == self.zone_name:
                continue
            elif rtype == 'SOA':
                continue

            rvalue = rdata.to_text()
            if (name, rtype, ttl) in rrecords:
                new_value = rrecords[(name, rtype, ttl)]
                new_value.append(rvalue)
                rrecords[(name, rtype, ttl)] = new_value
            else:
                rrecords[(name, rtype, ttl)] = [rvalue]

        return rrecords

    def _get_rrsets(self, ltype = None, lname = None):
        """Gets rrsets from route 53 starting with the name specified or if None, the beginning.
        Returns a simple bind representation of these records, the number of records retrieved and the
        type and the name of the last retrieved.
        Amazon only returns 100 at a time so this may need to be called multiple times to get the
        whole list.
        """

        simple_bind = ""
        last_name = None
        last_type = None
        number = 0
        for rrecord in self.conn.get_all_rrsets(self.id, ltype, lname):
            rtype = str(rrecord.type)
            name = str(rrecord.name)
            ttl = str(rrecord.ttl)
            simple_bind += "$TTL %s\n" % (ttl)

            for value in rrecord.resource_records:
                simple_bind += "%s\tIN\t%s\t%s\n" % (name, rtype, str(value))

            last_type = rtype
            last_name = name
            number += 1

        return simple_bind, number, last_type, last_name

    def _to_dnszone(self):
        """Gets all resource records from route 53 and parses them into a dns.zone object."""
        last_type = None
        last_name = None
        simple_bind = ""
        while True:
            rrset_batch, lines, ltype, lname = self._get_rrsets(last_type, last_name)
            simple_bind += rrset_batch
            if lines > 99:
                last_name = lname
                last_type == ltype
            else:
                break

        zone = dns.zone.from_text(simple_bind, origin=self.zone_name, relativize=False)
        return zone

    def create(self, zone_file, dry_run):
        """ Create the zone and populate with settings from the passed in zone_file.
        Do nothing, report only, if dry_run is true.
        """
        if self.id != None:
            log.error('A zone definition already exists for zone ' + self.zone_name)
            return
        
        log.info('Creating zone ' + self.zone_name)
        if not dry_run:
            zone = self.conn.create_hosted_zone(self.zone_name)['CreateHostedZoneResponse']
            nameservers = ""
            for nameserve in zone['DelegationSet']['NameServers']:
                nameservers += nameserve + ' '
            log.info('Zone nameservers: ' + nameservers)
            self.id = zone['HostedZone']['Id'].replace('/hostedzone/', '')
            zone_xml = self._create_xml(zone_file)
            #log.debug(zone_xml)
            log.info("Adding rrsets to zone " + self.zone_name)
            for xml in zone_xml:
                change = self.conn.change_rrsets(self.id, xml)
    
    def create_host(self, host, rtype, ttl, value):
        """Create a host entry in this zone."""
        xmlout = self.xml_header
        xmlout += self._add_change_xml('.'.join([host, self.zone_name]), rtype, ttl, [value, ])
        xmlout += self.xml_footer
        self.conn.change_rrsets(self.id, xmlout)
        log.debug("Updating %s %s %s to %s" % (host, rtype, ttl, value))

    def exists(self):
        """Return true if the self.zone_name exists on AWS, false otherwise."""
        if self.id != None:
            return True
        zones = self.conn.get_all_hosted_zones().values()[0]['HostedZones']
        for zone in zones:
            if zone['Name'][:-1] == self.zone_name: #strip the trailing .
                self.id = zone['Id'].replace('/hostedzone/', '')
                return True

        return False

    def get_host(self, host):
        """Return the (rtype, [values, ]) if the host exists in this domain on AWS, None otherwise."""
        for rrecord in self.conn.get_all_rrsets(self.id, name=host):
            log.debug(rrecord.name)
            if host == rrecord.name.split('.', 1)[0]:
                return (rrecord.type, rrecord.resource_records)

        return False


    def update(self, zone_file, dry_run):
        """Compare existing Resource Records to the given zone file and update if needed.
        Do nothing, report only, if dry_run is true.
        """
        if self.id == None:
            if not self.exists():
                log.error('The zone ' + self.zone_name + " doesn't exist, create it don't update.")
                return

        dnszone = dns.zone.from_file(zone_file, origin=self.zone_name, relativize=False)
        r53zone = self._to_dnszone()

        if dnszone == r53zone: #This compares SOA and root NS records, which are ignored in actual updates
            log.info('Zone %s is up to date.' % self.zone_name)
            return
    
        adds, deletes, updates = self._compare(r53zone, dnszone)
        changesets = self._create_changeset(adds, deletes, updates)
        if changesets is None:
            log.info("No differences found for zone %s" % self.zone_name)
            return

        log.info('Updating zone %s' % self.zone_name)
        if not dry_run:
            for changeset in changesets:
                change = self.conn.change_rrsets(self.id, changeset)

    def update_host(self, host, rtype, ttl, existing, value):
        """Updates a individual host entry in this zone."""
        xmlout = self.xml_header
        xmlout += self._update_change_xml('.'.join([host, self.zone_name]) , rtype, ttl, existing[1], [value, ])
        xmlout += self.xml_footer
        self.conn.change_rrsets(self.id, xmlout)
        log.debug("Updating %s %s %s to %s" % (host, rtype, ttl, value))

    def remove(self, dry_run):
        """Remove this zone from AWS."""
        if self.id == None:
            if not self.exists():
                log.info("Zone " + self.zone_name + " doesn't exist.")
                return

        log.info("Removing zone " + self.zone_name)
        if not dry_run:
            rrecords = self._get_rrecords(self._to_dnszone())
            
            xmllist = []
            rrecord_keys = rrecords.keys()
            rrecord_groups = [ rrecord_keys[n:n+100] for n in range(0, len(rrecord_keys), 100)]
            for rrecords_slice in rrecord_groups: 
                xml = self.xml_header
                
                change_needed = False #If only NS and SOA records just delete the zone
                for key in rrecords_slice:
                    name = key[0]
                    rtype = key[1]
                    ttl = key[2]
                    if rtype == 'NS' and name[:-1] == self.zone_name:
                        continue
                    elif rtype == 'SOA':
                        continue
                    change_needed = True
                    xml += self._delete_change_xml(name, rtype, ttl, rrecords[key])

                xml += self.xml_footer
                if change_needed:
                    xmllist.append(xml)

            for xml in xmllist:
                change = self.conn.change_rrsets(self.id, xml)
            delete = self.conn.delete_hosted_zone(self.id)
