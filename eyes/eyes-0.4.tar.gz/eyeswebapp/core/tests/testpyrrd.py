""" verifying functionality of pyrrd library"""
import datetime
import os
import unittest

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.util import epoch

DSNAME = 'testds'
RRDFILENAME = 'testrrd'
def create_base_rrd():
    dss = []
    rras = []
    ds1 = DS(dsName=DSNAME, dsType="GAUGE", heartbeat=600)
    dss.append(ds1)
    #86400 = 1 day, 604800 = 1 week, 2620800 = 1 month, 7862400 = 1 quarter
    # min, max, and average every 5 minutes for 3 months
    rra_5min_avg_qtr = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=26208)
    rras.append(rra_5min_avg_qtr) 
    # create initial RRD starting 1 day ago...
    just_a_bit_ago = epoch(datetime.datetime.now())-86400
    thisRRDfile = RRD(RRDFILENAME, ds=dss, rra=rras, step=300, start=just_a_bit_ago)
    thisRRDfile.create()

# def create_full_rrd():
#     dss = []
#     rras = []
#     ds1 = DS(dsName=DSNAME,dsType="GAUGE",heartbeat=600)
#     dss.append(ds1)
#     #86400 = 1 day, 604800 = 1 week, 2620800 = 1 month, 7862400 = 1 quarter
#     # min, max, and average every 5 minutes for 3 months
#     rra_5min_avg_qtr = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=26208)
#     rras.append(rra_5min_avg_qtr) 
#     rra_5min_min_qtr = RRA(cf='MIN', xff=0.5, steps=1, rows=26208)
#     rras.append(rra_5min_min_qtr)
#     rra_5min_max_qtr = RRA(cf='MAX', xff=0.5, steps=1, rows=26208)
#     rras.append(rra_5min_max_qtr)
#     # min, max, and average daily for 2 years
#     rra_daily_avg_2yr = RRA(cf='AVERAGE', xff=0.5, steps=288, rows=730)
#     rras.append(rra_daily_avg_2yr) 
#     rra_daily_min_2yr = RRA(cf='MIN', xff=0.5, steps=288, rows=730)
#     rras.append(rra_daily_min_2yr)
#     rra_daily_max_2yr = RRA(cf='MAX', xff=0.5, steps=288, rows=730)
#     rras.append(rra_daily_max_2yr)
#     # this takes up 633K per data source...
#     # create initial RRD starting 1 day ago...
#     just_a_bit_ago = epoch(datetime.datetime.now())-86400
#     thisRRDfile = RRD(RRDFILENAME, ds=dss, rra=rras, step=300, start=just_a_bit_ago)
#     thisRRDfile.create()
    
def nuke_base_rrd():
    if os.path.exists(RRDFILENAME):
        os.remove(RRDFILENAME)
    
class PyRRDTests(unittest.TestCase):
    """ pyrrd unit tests """

    def setUp(self):
        """set up for pyrrd verification"""
        nuke_base_rrd()
    #
    def test_setup_teardown(self):
        """testing set up and tear down"""
        self.assertFalse(os.path.exists(RRDFILENAME))
        create_base_rrd()
        self.assertTrue(os.path.exists(RRDFILENAME))
        nuke_base_rrd()
        self.assertFalse(os.path.exists(RRDFILENAME))
    #
    def test_inserting_data1(self):
        """testing basic insert and retrieval of data"""
        create_base_rrd()
        this_rrd = RRD(RRDFILENAME)
        # convert datetime object to seconds since epoch for RRD...
        timestamp = datetime.datetime.now()
        epoch_int = epoch(timestamp)
        this_rrd.bufferValue(epoch_int, 111)
        this_rrd.update()
        
        rrd2 = RRD(RRDFILENAME, mode="r")
        self.assertTrue(rrd2)
        # TODO: PYRRD_BROKEN
        # self.assertEquals(len(rrd2.ds),5)
        # data_dict1 = rrd2.ds[0].getData()
        # self.assertEquals(data_dict1['name'],DSNAME)
        # self.assertEquals(data_dict1['last_ds'],111)
    #
    def test_inserting_data2(self):
        """testing multiple insert and retrieval of data"""
        self.assertFalse(os.path.exists(RRDFILENAME))
        create_base_rrd()
        this_rrd = RRD(RRDFILENAME)
        # convert datetime object to seconds since epoch for RRD...
        now = datetime.datetime.now()
        min5ago = now-datetime.timedelta(minutes=5)
        min10ago = now-datetime.timedelta(minutes=10)
        now_int = epoch(now)
        min5ago_int = epoch(min5ago)
        min10ago_int = epoch(min10ago)
        this_rrd.bufferValue(min10ago_int, 412)
        this_rrd.bufferValue(min5ago_int, 512)
        this_rrd.bufferValue(now_int, 612)
        this_rrd.update()
        
        rrd2 = RRD(RRDFILENAME, mode="r")
        self.assertTrue(rrd2)
        # TODO: PYRRD_BROKEN
        # self.assertEquals(len(rrd2.ds),1)
        # data_dict1 = rrd2.ds[0].getData()
        # self.assertEquals(data_dict1['name'],DSNAME)
        # self.assertEquals(data_dict1['last_ds'],612)    
    #
    
if __name__ == '__main__':  # pragma: no cover
    suite = unittest.TestLoader().loadTestsFromTestCase(PyRRDTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    