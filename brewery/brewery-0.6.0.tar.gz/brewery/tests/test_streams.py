import unittest
import brewery
import csv
import os
from common import TESTS_PATH

class SourceDataStreamTestCase(unittest.TestCase):
    output_dir = None
    @classmethod
    def setUpClass(cls):
        SourceDataStreamTestCase.output_dir = 'test_out'
        if not os.path.exists(SourceDataStreamTestCase.output_dir):
            os.makedirs(SourceDataStreamTestCase.output_dir)
    @classmethod
    def tearDownClass(cls):
        pass
        
    def setUp(self):
        self.data_dir = os.path.join(TESTS_PATH, 'data')
        self.output_dir = SourceDataStreamTestCase.output_dir

        handle = open(os.path.join(self.data_dir, "test.csv"))
        reader = csv.reader(handle)

        self.field_names = reader.next()
        self.fields = brewery.ds.fieldlist(self.field_names)
        
        self.rows = []
        self.records = []
        self.expanded_records = []
        for row in reader:
            self.rows.append(row)
            record = dict(zip(self.field_names, row))
            self.records.append(record)
            record = brewery.ds.expand_record(record)
            self.expanded_records.append(record)
            
        handle.close()


    def data_file(self, file):
        return os.path.join(self.data_dir, file)
    def output_file(self, file):
        return os.path.join(self.output_dir, file)
    
    # def test_1(self):
    #     self.assertEqual(1, 23)
        
# class CSVDataStreamsTestCase(SourceDataStreamTestCase):
#     """docstring for CSVDataStreamsTestCase"""
#         
#     def setUp(self):
#         super(CSVDataStreamsTestCase, self).setUp()
#         self.source = CSVSourceStream
#         
#     def test_2(self):
#         self.assertEqual(1, 2)