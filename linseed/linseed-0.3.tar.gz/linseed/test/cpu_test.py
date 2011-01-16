import unittest

from linseed import CPU

class Test(unittest.TestCase):
    def test_count(self):
        CPU.count()

    def test_util(self):
        for cpuid in range(CPU.count()):
            CPU(cpuid).utilization()
            CPU(cpuid).utilization(0.2345)
