# -*- coding: latin-1 -*-
import unittest

from django.db import models
from models import LocationBase

class MyLocation(LocationBase):
    text = models.CharField(max_length=30)

class LocationTests(unittest.TestCase):

    def setUp(self):
        # found positions using http://www.gorissen.info/Pierre/maps/googleMapLocationv3.php
        self.porsgrunn = MyLocation.objects.create(text="Porsgrunn", latitude=59.146361, longitude=9.651489)
        self.skien = MyLocation.objects.create(text="Skien", latitude=59.218123, longitude=9.604797)
        self.nenset = MyLocation.objects.create(text="Nenset", latitude=59.170298, longitude=9.629860)
        self.hovenga = MyLocation.objects.create(text="Hovenga", latitude=59.147241, longitude=9.665909)
        self.heistad = MyLocation.objects.create(text="Heistad", latitude=59.077095, longitude=9.691315)
        self.brevik = MyLocation.objects.create(text="Brevik", latitude=59.055740, longitude=9.699211)
        self.langesund = MyLocation.objects.create(text="Langesund", latitude=59.001147, longitude= 9.746246)

    def tearDown(self):
        self.porsgrunn.delete()
        self.skien.delete()
        self.nenset.delete()
        self.hovenga.delete()
        self.heistad.delete()
        self.brevik.delete()
        self.langesund.delete()

    def test_hovenga_close_to_porsgrunn(self):
        self.assertTrue(self.hovenga.id in [loc.id for loc in MyLocation.items_in_radius(self.porsgrunn.latitude, self.porsgrunn.longitude, radius = 5).all()])

    def test_langesund_is_not_close_to_porsgrunn(self):
        self.assertFalse(self.langesund.id in [loc.id for loc in MyLocation.items_in_radius(self.porsgrunn.latitude, self.porsgrunn.longitude, radius = 5).all()])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(LocationTests)
    unittest.TextTestRunner(verbosity=2).run(suite)