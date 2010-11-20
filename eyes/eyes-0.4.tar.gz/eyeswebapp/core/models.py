"""
Eyes Core Models
================

* models supporting the core monitoring infrastructure

"""
from django.db import models
from util.monitor import ArgSet
from util.monitor import validate_poller_results, validate_return_dictionary
import simplejson
import datetime
import dateutil.parser
import os
from settings import RRDFILE_ROOT
from settings import PNGFILE_ROOT
from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, VDEF #, CDEF 
from pyrrd.graph import LINE, AREA #, GPRINT
from pyrrd.graph import ColorAttributes, Graph
from pyrrd.util import epoch

class Host(models.Model):
    """ class representing a host. A host may have 0 or more associated monitors.
    
    >>> from core.models import Host
    >>> x = Host()
    >>> x.hostname="localhost"
    >>> x.save()
    >>> x
    <Host: localhost>
    >>> x.monitor_set.count()
    0
    
    """
    # pylint: disable=E1101
    hostname = models.CharField(max_length=250, default="localhost")
    
    class Meta:
        """META class for Django model administration - basic ordering, naming."""
        ordering = ['hostname']
        verbose_name, verbose_name_plural = "Host", "Hosts"

    def __unicode__(self):
        """unicode string representation of a Monitor"""
        return u"%s" % (self.hostname, )

    @models.permalink
    def get_absolute_url(self):
        """ returns the absolute URL for the monitor element"""
        return ('core.views.host_detail', [str(self.id)])

class MonitorManager(models.Manager):
    """ manager object for manipulating monitor elements"""
    # pylint: disable=E1101
    def pending_update(self):
        """ returns the iterable django query set containing monitor objects that are due for updating.
        i.e. Monitor.objects.pending_update()
        """
        basic_set = self.get_query_set().exclude(passive__exact=True).exclude(nextupdate__gte=datetime.datetime.now())
        return basic_set

class Monitor(models.Model):
    """A monitor in the Eyes system
    
    >>> from core.models import Monitor
    >>> from util.monitor import ArgSet
    >>> x = Monitor()
    >>> x.name="selfping"
    >>> x.plugin_name="check_ping"
    >>> args = ArgSet()
    >>> args.add_argument_pair("-H", "localhost")
    >>> args.add_argument_pair("-w", "1,99%")
    >>> args.add_argument_pair("-c", "1,99%")
    >>> x.arg_set = args
    >>> x.save()
    >>> x
    <Monitor: Monitor selfping (check_ping) against None>
    >>> x.json_argset
    '[{"-H": "localhost"}, {"-w": "1,99%"}, {"-c": "1,99%"}]'
    
    """
    # pylint: disable=E1101
    STATE_CHOICES = (
        (0, u'ok'), 
        (1, u'warning'),
        (2, u'error'),
        (3, u'unknown'),
    )

    objects = MonitorManager()
    #
    name = models.CharField(max_length=250, default='') # user specified name
    plugin_name = models.CharField(max_length=250, default="check_ping") #names of nagios plugins - like check_snmp
    json_argset = models.TextField(blank=True) #json representation of an ArgSet
    #
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    #
    poll_frequency = models.IntegerField(default=5) # value in minutes
    lastupdate = models.DateTimeField(null=True) # to be queried to determine what needs to be updated
    nextupdate = models.DateTimeField(null=True, db_index=True) #denormalized data to make querying against a narrower gap more effective - to be set on each update based on freq requested
    # state information - denormalized into this immediate state and previous run list as a sep. model?
    latest_state = models.SmallIntegerField(default=0, choices=STATE_CHOICES)
    latest_result_string = models.CharField(max_length=255, blank=True)
    #
    alerting = models.BooleanField(default=True)
    passive = models.BooleanField(default=False, db_index=True) # identifies a passive monitor
    #
    host = models.ForeignKey(Host, null=True)

    # reconfigured to use python properties to return an util.monitor.ArgSet object from JSON data store
    def _get_arg_set(self):
        """ returns an argument set (ArgSet) object for a given monitor, None by default"""
        if self.json_argset is None:
            return None
        if self.json_argset == '':
            return None
        new_arg_set = ArgSet()
        new_arg_set.loadjson(self.json_argset)
        return new_arg_set
    def _set_arg_set(self, arg_set):
        """ takes an ArgSet object (NagiosInvoker argument set) and stores it into the monitor 
        as the ArgSet's JSON representation"""
        if (arg_set is None):
            self.json_argset = ''
        else:
            self.json_argset = arg_set.json()
    arg_set = property(_get_arg_set, _set_arg_set)
                    
    def _get_state(self):
        """ returns the latest state of the monitor """
        return self.latest_state
    def _set_state(self, incoming_state):
        """ updates the lastupdate and nextupdate timestamp on the object.
        (0, u'ok') -- state is OK according to threshold or monitor
        (1, u'warning') -- warning: not OK, but not error either
        (2, u'error') -- something's gone very off expectations
        (3, u'unknown') -- used for monitors that just collect metrics without analysis, or prior to any collection
        """
        now = datetime.datetime.now()
        self.lastupdate = now
        if not(self.passive):
            self.nextupdate = now+datetime.timedelta(minutes=self.poll_frequency)
        if (incoming_state >= 0) and (incoming_state < 4):
            self.latest_state = incoming_state
    state = property(_get_state, _set_state)

    def _get_state_display(self):
        for key, strvalue in Monitor.STATE_CHOICES:
            if self.latest_state == key:
                return strvalue
    state_display = property(_get_state_display)
    
    def store_dict_results(self, result_dict, debug=None):
        """ validate the dictionary structure results from the poller. If kosher, then use the returncode
        to set the current state for this monitor. Returns "True" if data passed validation
        and was stored.
        """
        validated = validate_return_dictionary(result_dict)
        if (validated):
            self.state = result_dict['returncode']
            self.latest_result_string = result_dict['decoded']['human']
            decoded = result_dict['decoded']
            keylist = decoded.keys()
            keylist.remove('human')
            for key in keylist:
                if (debug):
                    print "getting datastore named %s" % key
                (datastore, created_newds) = Datastore.objects.get_or_create(monitor=self, name=key)
                if (created_newds):
                    datastore.save()
                    datastore.create_rrd(overwrite=True)
                    if (debug):
                        print "!!! Created datastore for name %s" % key
                        print "!!! generated RRD file %s for key %s (id is %s)" % (datastore.location, key, datastore.id)
                insertvalue = decoded[key]['value']
                # convert timestamp from string to datetime object
                timestamp = dateutil.parser.parse(result_dict['timestamp'])
                if (debug):
                    print "Inserting %s into datastore %s for key %s (datastore name is %s)" % (insertvalue, datastore.location, key, datastore.name)
                datastore.insert_data(timestamp, insertvalue)
                datastore.save()
            self.save()
            return True
        return False
            
    def store_json_results(self, json_result_dict, debug=None):
        """ validate the JSON results from the poller. If kosher, then use the returncode
        to set the current state for this monitor. Returns "True" if data passed validation
        and was stored.
        """
        if (debug):
            print "!!! attempting to store data %s" % json_result_dict
        validated = validate_poller_results(json_result_dict)
        if (validated):
            if (debug):
                print "!!! data has been validated"
            result_dict = simplejson.loads(json_result_dict)
            return self.store_dict_results(result_dict, debug)
    
    class Meta:
        """META class for Django model administration - basic ordering, naming."""
        verbose_name, verbose_name_plural = "Monitor", "Monitors"

    def __unicode__(self):
        """unicode string representation of a Monitor"""
        return u"Monitor %s (%s) against %s" % (self.name, self.plugin_name, self.host)

    @models.permalink
    def get_absolute_url(self):
        """ returns the absolute URL for the monitor element"""
        return ('core.views.monitor_detail', [str(self.id)])

class DatastoreManager(models.Manager):
    """ manager object for manipulating data store elements"""
    # def pending_update(self):
    #     """ returns the iterable django query set containing monitor objects that are due for updating"""
    #     basic_set = self.get_query_set().exclude(nextupdate__gte=datetime.datetime.now())
    #     return basic_set

class Datastore(models.Model):
    """ represents a set of data storage - backed by any number of different things.
    RRDtool data - direct into a database - etc
    Intended to represent a time-series set of numeric values (decimal, int, float, etc)
    """
    # pylint: disable=E1101
    objects = DatastoreManager()
    
    #GAUGE', 'COUNTER', 'DERIVE', 'ABSOLUTE', 'COMPUTE'
    DSTYPE_CHOICES = (
        ('GAUGE', u'Gauge'), 
        ('COUNTER', u'Counter'),
        ('DERIVE', u'Derive'),
        ('ABSOLUTE', u'Absolute'),
        ('COMPUTE', u'Compute'),
    )
    
    monitor = models.ForeignKey(Monitor)
    name = models.CharField(max_length=18) # name of data store - max 18 characters for RRD
    dstype = models.CharField(max_length=8, choices=DSTYPE_CHOICES, default='GAUGE')
    heartbeat = models.IntegerField(default=600)
    step = models.IntegerField(default=300)
    # TODO: IF ANY OF THESE VALUES ARE CHANGED, THE RRD FILE FOR THE DATASTORE ID SHOULD BE RECREATED
    # TODO: OTHERWISE THINGS WILL LIKELY BREAK ON STORAGE
    
    def _get_location(self):
        if self.id is None:
            return None
        else:
            first_level = "%d" % (self.id%10)
            id_string = "%d.rrd" % self.id
            base_path = os.path.join(RRDFILE_ROOT, first_level)
            full_path = os.path.join(base_path, id_string)
            if not(os.path.exists(base_path)):
                os.mkdir(base_path)
            return full_path
    location = property(_get_location)
    
    def _rrd_exists(self):
        return os.path.exists(self.location)
    rrd_exists = property(_rrd_exists)
    
    def _make_rrd_file(self):
        dss = []
        rras = []
        ds1 = DS(dsName=self.name, dsType=self.dstype, heartbeat=self.heartbeat)
        dss.append(ds1)
        #86400 = 1 day, 604800 = 1 week, 2620800 = 1 month, 7862400 = 1 quarter
        # min, max, and average every 5 minutes for 3 months
        rra_5min_avg_qtr = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=26208)
        rras.append(rra_5min_avg_qtr) 
        rra_5min_min_qtr = RRA(cf='MIN', xff=0.5, steps=1, rows=26208)
        rras.append(rra_5min_min_qtr)
        rra_5min_max_qtr = RRA(cf='MAX', xff=0.5, steps=1, rows=26208)
        rras.append(rra_5min_max_qtr)
        # min, max, and average daily for 2 years
        rra_daily_avg_2yr = RRA(cf='AVERAGE', xff=0.5, steps=288, rows=730)
        rras.append(rra_daily_avg_2yr) 
        rra_daily_min_2yr = RRA(cf='MIN', xff=0.5, steps=288, rows=730)
        rras.append(rra_daily_min_2yr)
        rra_daily_max_2yr = RRA(cf='MAX', xff=0.5, steps=288, rows=730)
        rras.append(rra_daily_max_2yr)
        # this takes up 633K per data source...
        just_a_bit_ago = epoch(datetime.datetime.now())-86400
        thisRRDfile = RRD(self.location, ds=dss, rra=rras, step=self.step, start=just_a_bit_ago)
        thisRRDfile.create()
    
    def _png_path(self):
        if self.id is None:
            return None
        else:
            first_level = "%d" % (self.id%10)
            base_path = os.path.join(PNGFILE_ROOT, first_level)
            if not(os.path.exists(base_path)):
                os.mkdir(base_path)
            return base_path
    png_path = property(_png_path)
    
    def create_rrd(self, overwrite=False):
        """ creates an RRD file"""
        if os.path.exists(self.location):
            if (overwrite):
                self._make_rrd_file()
                return True
            else:
                return False
        else:
            self._make_rrd_file()
            return True

    def insert_data(self, timestamp, value):
        """
        responsible for inserting data (value) at the given timestamp (timestamp) into the RRD file associated
        with this datastore.
        
        This method will create an RRD file if it doesn't already exist
        """
        if not(self.rrd_exists):
            self.create_rrd()
            print "WARNING::: had to create RRD %s (ds is %s)" % (self.location, self.name, )
        this_rrd = RRD(self.location)
        # convert datetime object to seconds since epoch for RRD...
        epoch_int = epoch(timestamp)
        this_rrd.bufferValue(epoch_int, value)
        this_rrd.update()
    
    def generate_rrd_graph(self, duration=None, width=None, height=None, name_extension=None, location=None):
        """
        duration - # of seconds back to graph
        width - width of image generated
        height - height of image generated
        name_extension - graph name is id.png, name extension adds in 1-extension.png
        location = location for PNG file
        debug = enable print debugging
        
        TODO: do we want to enable color selection in through the method?
        """
        # set up objects to be displayed in graph...
        def1 = DEF(rrdfile=self.location, vname='example', dsName=self.name)
        vdef1 = VDEF(vname='myavg', rpn='%s,AVERAGE' % def1.vname)
        area1 = AREA(defObj=def1, color="#FFA902", legend=self.name)
        line1 = LINE(defObj=vdef1, color="#01FF13", legend='Average', stack=True)
        # set up graph details - colors, name, duration, size
        cattr = ColorAttributes()
        cattr.back = '#333333'
        cattr.canvas = '#333333'
        cattr.shadea = '#000000'
        cattr.shadeb = '#111111'
        cattr.mgrid = '#CCCCCC'
        cattr.axis = '#FFFFFF'
        cattr.frame = '#AAAAAA'
        cattr.font = '#FFFFFF'
        cattr.arrow = '#FFFFFF'
            
        graphname = '%s.png' % (self.id)
        if (name_extension):
            graphname = '%s-%s.png' % (self.id, name_extension)        
        graphfile = graphname
        graphfile = os.path.join(self.png_path, graphname)
        if (location):
            graphfile = os.path.join(location, graphname)
            
        # Now that we've got everything set up, let's make a graph
        # default - 1 day
        now = datetime.datetime.now()
        endtime = epoch(now)
        day = 24 * 60 * 60
        starttime = endtime - day
        if (duration):
            starttime = endtime - duration
        # create the graph
        g = Graph(graphfile, start=starttime, end=endtime, vertical_label=self.name, color=cattr)
        if (width):
            g.width = width
        if (height):
            g.height = height
        g.data.extend([def1, vdef1, area1])
        g.write()
        
    class Meta:
        """META class for Django model administration - basic ordering, naming."""
        ordering = ['name']

    def __unicode__(self):
        """unicode string representation of a Datastore"""
        return u"Datastore %s for %s" % (self.name, self.monitor)

    @models.permalink
    def get_absolute_url(self):
        """ returns the absolute URL for the monitor element"""
        return ('core.views.datastore_detail', [str(self.id)])
    