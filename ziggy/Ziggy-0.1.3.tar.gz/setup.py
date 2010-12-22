from distutils.core import setup, Command
import distutils.sysconfig
import os, sys

class HadoopCommand(Command):
    description = "Command which sets Hadoop configuration options."
    user_options=[]
    hadoop_home = "/usr/local/hadoop/" # The root directory of the hadoop installation
    hadoop = hadoop_home + "bin/hadoop" #/the location of the hadoop executable
    hadoop_streaming = hadoop_home + "contrib/streaming/hadoop-0.20.2-streaming.jar" #the location of that hadoop streaming jar
    num_map_tasks=20 #the number of map tasks currently configured
    shared_tmp_space = hadoop_home+"user-tmp/"
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        installation_dir = distutils.sysconfig.get_python_lib()
        assert os.getcwd() == self.cwd, "Must be in package root %s" % self.cwd
        hadoop_config_file = open(self.cwd+"/ziggy/hdmc/hadoop_config.py", "w")
        print >> hadoop_config_file, "hadoop_home='"+self.hadoop_home+"'"
        print >> hadoop_config_file, "hadoop='"+self.hadoop+"'"
        print >> hadoop_config_file, "hadoop_streaming='"+self.hadoop_streaming+"'"
        print >> hadoop_config_file, "num_map_tasks="+str(self.num_map_tasks)
        print >> hadoop_config_file, "shared_tmp_space='"+self.shared_tmp_space+"'"
        print >> hadoop_config_file, "GraphReduce_location='"+installation_dir+"/ziggy/GraphReduce'"
        hadoop_config_file.close()
        os.system("chmod a+rwx "+self.cwd+"/ziggy/hdmc/hadoop_config.py")
        os.system("cp "+self.cwd+"/ziggy/hdmc/hadoop_config.py " + self.cwd+"/ziggy/hdmc/hdfs/hdfs_config.py")
        os.system("cp "+ self.cwd+"/ziggy/hdmc/hadoop_config.py " + self.cwd+"/ziggy/GraphReduce/hadoop_config.py ")


        
setup(
    name='Ziggy',
    version='0.1.3',
    author='Daniel McClary',
    author_email='dan.mcclary@northwestern.edu',
    packages=['ziggy', 'ziggy.hdmc', 'ziggy.hdmc.hdfs', 'ziggy.hdmc.test', 'ziggy.GraphReduce'],
    url='http://pypi.python.org/pypi/Ziggy/',
    license='LICENSE.txt',
    description='Python modules for Hadoop Streaming',
    long_description=open('README.txt').read(),
    cmdclass={'hadoop':HadoopCommand},
)
