'''
Created on Jul 29, 2010

@author: dwmclary
'''
import unittest
import os
import hdmc
import hdfs.hdfs_access as hdfs
import hadoop_config as config
from glob import glob

class HDMCTest(unittest.TestCase):
    def runTest(self):
        self.setUp()
        self.testSubmitNoSupportingFiles()
        self.tearDown()

    def setUp(self):
        self.wd = os.getcwd()
        self.script = self.wd+"/test/numpy_random_means.py"
        self.reducer = self.wd+"/test/numpy_mean_reduction.py"
        self.output_file = self.wd+"/test/random_means"
        self.checkpoint_names = map(str, range(1,20))
        self.checkpoint_dir = config.shared_tmp_space+os.getlogin()+"/hdmc_checkpoints"
        pass


    def tearDown(self):
        pass


    def testMakeFrame(self):
        hdmc.make_frame(self.script)
        self.assertTrue(os.path.isfile(self.wd+"/frame.py"))
        
    def testMakeCheckpointFrame(self):
        hdmc.make_checkpointing_frame(self.script, self.checkpoint_names, self.checkpoint_dir)
        self.assertTrue(os.path.isfile(self.wd+"/checkpoint_frame.py"))
        
    def testCreateDummyData(self):
        hdfs.rm("dummy")
        hdmc.create_dummy_data()
        dummy_data = hdfs.cat("dummy")["stdout"]
        self.assertEqual("dummy data", dummy_data.rstrip())
        
    def testSetCheckpointDirectory(self):
        os.system('rmdir '+self.checkpoint_dir)
        checkpoint_dir = hdmc.set_checkpoint_directory(self.output_file)
        self.assertTrue(os.path.exists(checkpoint_dir))
        
    def testDownloadHDFSData(self):
        hdmc.download_hdfs_data(self.wd+"/test/dummy")
        self.assertTrue(os.path.isfile(self.wd+"/test/dummy"))
        os.system('rm '+self.wd+'/test/dummy')
        self.assertFalse(os.path.isfile(self.wd+"/test/dummy"))
        
    def testSubmitNoSupportingFiles(self):
        hdfs.rm("random_means")
        hdmc.submit_inline(self.script, self.output_file, iterations=200)
        self.assertTrue(os.path.exists(self.wd+"/test/random_means"))    
        
    def testSubmitReductionNoSupportingFiles(self):
        hdfs.rm("random_means")
        hdmc.submit_inline(self.script, self.output_file, iterations=200, reduction_script = self.reducer)
        self.assertTrue(os.path.exists(self.wd+"/test/random_means"))
        
    def testSubmitCheckpoints(self):
        hdfs.rm("line_counts")
        file_list = glob(self.wd+"/test/gutenberg/*")
        self.script = self.wd+"/test/line_counter.py"
        self.output_file = self.wd+"/test/line_counts"
        checkpoints = hdmc.submit_checkpoint_inline(self.script, self.output_file, file_list, "")
        self.assertEqual(len(file_list), len(checkpoints))
        self.assertTrue(os.path.exists(self.wd+"/test/line_counts"))
        hadoop_result_file = self.wd+"/test/line_counts"
        master_result_file = self.wd+"/test/wc_output.dat"
        hadoop_results = {}
        master_results = {}

        for line in open(master_result_file).readlines():
            if len(line.rstrip()) > 0:
                entry = line.split()
                master_results[entry[1]] = int(entry[0])
        for line in open(hadoop_result_file).readlines():
            if len(line.rstrip()) > 0:
                entry = line.split()
                hadoop_results[entry[1]] = int(entry[0])

        for key in master_results.keys():
            self.assertEqual(master_results[key], hadoop_results[key])
        
    def testSubmitCheckpointsReduce(self):
        hdfs.rm("line_total")
        file_list = glob(self.wd+"/test/gutenberg/*")
        self.script = self.wd+"/test/line_counter.py"
        self.output_file = self.wd+"/test/line_total"
        self.reducer = self.wd+"/test/line_sum.py"
        checkpoints = hdmc.submit_checkpoint_inline(self.script, self.output_file, file_list, reduction_script = self.reducer, arguments="")
        self.assertEqual(len(file_list), len(checkpoints))
        self.assertTrue(os.path.exists(self.wd+"/test/line_total"))
        hadoop_result_file = self.wd+"/test/line_total"
        master_result_file = self.wd+"/test/wc_total.dat"
        hadoop_results = {}
        master_results = {}
        for line in open(master_result_file).readlines():
            if len(line.rstrip()) > 0:
                entry = line.split()
                master_results[entry[1]] = int(entry[0])
        for line in open(hadoop_result_file).readlines():
            if len(line.rstrip()) > 0:
                entry = line.split()
                hadoop_results[entry[1]] = int(entry[0])
        for key in master_results.keys():
            self.assertEqual(master_results[key], hadoop_results[key])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()