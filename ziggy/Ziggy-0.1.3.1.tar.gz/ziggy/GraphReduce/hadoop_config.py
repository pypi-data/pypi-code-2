'''
Created on May 17, 2010
Generic configuration parameters for Hadoop-based python modules
@author: dwmclary
'''


hadoop_home = "/usr/local/hadoop/" # The root directory of the hadoop installation
hadoop = hadoop_home + "bin/hadoop" #/the location of the hadoop executable
hadoop_streaming = hadoop_home + "contrib/streaming/hadoop-0.20.2-streaming.jar" #the location of that hadoop streaming jar
num_map_tasks=20 #the number of map tasks currently configured
GraphReduce_location = "/home/staff/dwmclary/workspace/GraphReduce/src/GraphReduce/"
