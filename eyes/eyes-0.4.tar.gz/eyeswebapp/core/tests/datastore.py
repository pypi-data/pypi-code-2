"""
This file stores all the tests related to the Datastore model
"""
from django.test import TestCase
from core.models import Datastore
from core.models import Monitor
from eyeswebapp.util.monitor import ArgSet
import datetime
import os
from settings import RRDFILE_ROOT
from settings import PNGFILE_ROOT
from core.tests.util import create_unsaved_datastore
from core.tests.util import create_unsaved_minimum_monitor
from core.tests.util import clear_all_rrd_files
from pyrrd.rrd import RRD

class DatastoreTests(TestCase):
    """ tests for the Datastore model"""
    def tearDown(self):
        """testing default datastore model data"""
        clear_all_rrd_files()

    def setUp(self):
        """testing default datastore model data"""
        clear_all_rrd_files()
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        self.datastore = create_unsaved_datastore()
        
    def test_default_data(self):
        """testing default datastore model data & setUp"""
        ds = self.datastore
        self.assertTrue(ds)
        self.assertEquals(ds.name, 'pl')
        self.assertEquals(ds.monitor.name, 'newmonitor')

    def test_default_unicodevalue(self):
        """testing default datastore - unicode repr"""
        ds = self.datastore
        self.assertEquals(ds.__unicode__(), u'Datastore pl for Monitor newmonitor (check_ping) against None')

    def test_default_data2(self):
        """testing default datastore model data"""
        ds = self.datastore
        mon = ds.monitor
        new_ds = Datastore(monitor=mon)
        self.assertTrue(new_ds)
        self.assertEquals(new_ds.name, '')
        self.assertEquals(new_ds.dstype, 'GAUGE')
        self.assertEquals(new_ds.heartbeat, 600)
        self.assertEquals(new_ds.step, 300)

    def test_reverse_url_setup(self):
        """testing reverse url lookup for a datastore model object"""
        # pylint: disable=E1101
        ds1 = self.datastore
        ds1.save()
        uri = "/core/datastore/%d/" % ds1.id
        self.assertEquals(ds1.get_absolute_url(), uri)

    def test_datastore_linkage(self):
        """testing datastore linkage to monitors"""
        # pylint: disable=E1101
        ds1 = self.datastore
        ds1.save()
        mon = ds1.monitor
        new_ds11 = Datastore(monitor=mon, name="foo").save()
        new_ds12 = Datastore(monitor=mon, name="bar").save()
        list_of_ds1 = mon.datastore_set.all()
        self.assertEquals(len(list_of_ds1), 3)
    #
    def test_functional_location(self):
        """ validating default location values"""
        self.assertTrue(os.path.exists(RRDFILE_ROOT))
        self.assertTrue(os.path.isdir(RRDFILE_ROOT))
    #
    def test_datastore_location(self):
        """ validating location set for RRD file"""
        # pylint: disable=E1101
        ds1 = self.datastore
        self.assertEquals(ds1.location, None)
        ds1.save()
        first_level = "%d" % (ds1.id%10)
        id_string = "%d.rrd" % ds1.id
        full_expected_path = os.path.join(RRDFILE_ROOT, first_level, id_string)
        self.assertEquals(ds1.location, full_expected_path)
    #
    def test_functional_rrd_creation(self):
        """ functional testing of creation of RRD files"""
        # pylint: disable=E1101
        clear_all_rrd_files()
        ds1 = self.datastore
        ds1.save()
        self.assertTrue(ds1.location)
        self.assertEquals(ds1.rrd_exists, False)
        result = ds1.create_rrd()
        self.assertTrue(result)
        self.assertTrue(ds1.rrd_exists)
        # attempt to create it again, without spec overwrite
        result = ds1.create_rrd()
        self.assertFalse(result)
        self.assertTrue(ds1.rrd_exists)
        # force a recreation of the RRD file
        result = ds1.create_rrd(overwrite=True)
        self.assertTrue(result)
        self.assertTrue(ds1.rrd_exists)
    #
    def test_functional_datastore_RRD1(self):
        """ test functional RRD elements from datastore creation """
        clear_all_rrd_files()
        ds1 = self.datastore
        ds1.save()
        self.assertTrue(ds1)
        self.assertEquals(ds1.name,'pl')
        self.assertFalse(ds1.rrd_exists)
        ds1.create_rrd()
        self.assertTrue(ds1.rrd_exists)
        timestamp = datetime.datetime.now()
        ds1.insert_data(timestamp, '101')
        #mode='r' is a slow method - loads data from the RRD file
        rrd1 = RRD(ds1.location, mode="r")
        self.assertTrue(rrd1)
        # self.assertEquals(len(rrd1.ds),1)
        # data_dict1 = rrd1.ds[0].getData()
        # self.assertEquals(data_dict1['name'],'pl')
        # self.assertEquals(data_dict1['last_ds'],101)
    #
    def test_functional_datastore_RRD2(self):
        """ test inserting data into RRD when it doesn't exist """
        clear_all_rrd_files()
        ds1 = self.datastore
        ds1.save()
        self.assertTrue(ds1)
        self.assertEquals(ds1.name, 'pl')
        self.assertFalse(ds1.rrd_exists)
        min_now = datetime.datetime.now()
        ds1.insert_data(min_now, '59')
        #mode='r' is a slow method - loads data from the RRD file
        rrd2 = RRD(ds1.location, mode="r")
        self.assertTrue(rrd2)
        # self.assertEquals(len(rrd2.ds),1)
        # data_dict1 = rrd2.ds[1].getData()
        # self.assertEquals(data_dict1['name'],'pl')
        # self.assertEquals(data_dict1['last_ds'],43)
    #
    def test_functional_datastore_RRD3(self):
        """ test generation of RRD graph """
        # pylint: disable=E1101
        clear_all_rrd_files()
        ds1 = self.datastore
        ds1.save()
        self.assertTrue(ds1)
        self.assertEquals(ds1.name,'pl')
        self.assertFalse(ds1.rrd_exists)
        now = datetime.datetime.now()
        min_30_ago = now-datetime.timedelta(minutes=30)
        min_25_ago = now-datetime.timedelta(minutes=25)
        min_20_ago = now-datetime.timedelta(minutes=20)
        min_15_ago = now-datetime.timedelta(minutes=15)
        min_10_ago = now-datetime.timedelta(minutes=10)
        min_5_ago = now-datetime.timedelta(minutes=5)
        ds1.insert_data(min_30_ago, 60)
        ds1.insert_data(min_25_ago, 55)
        ds1.insert_data(min_20_ago, 50)
        ds1.insert_data(min_15_ago, 45)
        ds1.insert_data(min_10_ago, '40')
        ds1.insert_data(min_5_ago, '35')
        ds1.insert_data(now, '30')
        self.assertTrue(ds1.rrd_exists)
        ds1.generate_rrd_graph(location="/tmp")
        name = "%s.png" % ds1.id
        path_to_file = os.path.join("/tmp", name)
        self.assertTrue(os.path.exists(path_to_file))
        os.remove(path_to_file)
        self.assertFalse(os.path.exists(path_to_file))
    #
    def test_datastore_pngpath(self):
        """ test png path calculation """
        # pylint: disable=E1101
        clear_all_rrd_files()
        ds1 = self.datastore
        ds1.save()
        first_level = "%d" % (ds1.id%10)
        full_expected_path = os.path.join(PNGFILE_ROOT, first_level)    
        self.assertEquals(ds1.png_path, full_expected_path)
    