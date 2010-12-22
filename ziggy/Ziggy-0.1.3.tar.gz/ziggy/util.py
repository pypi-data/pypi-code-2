import os
import subprocess
from . import hdmc
from hdmc import hdfs
from . hdmc.code_generator import CodeGenerator

tmp_directory = "/tmp"
__all__ = ["sort_numeric", "sort_ascii", "search", "histogram"]


def make_histogram_frame():
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("import sys\n\n")
    c.write("def read_input(file):\n")
    c.indent()
    c.write("for line in file:\n")
    c.indent()
    c.write("yield line.strip()\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("data = read_input(sys.stdin)\n")
    c.write("for line in data:\n")
    c.indent()
    c.write("if len(line)>0:\n")
    c.indent()
    c.write("print 'ValueHistogram:'+line+':'+'1'\n")
    c.dedent()
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    frame_file = open("histogram_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx histogram_frame.py")
    
def make_counting_frame():
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("from collections import defaultdict\n")
    c.write("import sys\n\n")
    c.write("def read_input(file):\n")
    c.indent()
    c.write("for line in file:\n")
    c.indent()
    c.write("yield line.strip()\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("data = read_input(sys.stdin)\n")
    c.write("c = defaultdict(int)\n")
    c.write("for line in data:\n")
    c.indent()
    c.write("if len(line)>0:\n")
    c.indent()
    c.write("c[line] += 1\n")
    c.dedent()
    c.dedent()
    c.write("for key in c.keys():\n")
    c.indent()
    c.write("print 'ValueHistogram:'+key+':'+str(c[key])\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    frame_file = open("histogram_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx histogram_frame.py")
    
def make_grep_frame():
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("import sys\n\n")
    c.write("def read_input(file, pattern):\n")
    c.indent()
    c.write("line_count = 0\n")
    c.write("for line in file:\n")
    c.indent()
    c.write("line_count += 1\n")
    c.write("if pattern in line.strip():\n")
    c.indent()
    c.write("yield line.strip()\n")
    c.dedent()
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("search_pattern = open('ziggy_search').readline().strip()\n")
    c.write("data = read_input(sys.stdin, search_pattern)\n")
    c.write("for line in data:\n")
    c.indent()
    c.write("print line\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    frame_file = open("search_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx search_frame.py")
    
def make_search_frame(suppress_lines):
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("import sys\n\n")
    c.write("def read_input(file, pattern):\n")
    c.indent()
    c.write("line_count = 0\n")
    c.write("for line in file:\n")
    c.indent()
    c.write("line_count += 1\n")
    c.write("if pattern in line.strip():\n")
    c.indent()
    c.write("yield line.strip(), line_count\n")
    c.dedent()
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("search_pattern = open('ziggy_search').readline().strip()\n")
    c.write("data = read_input(sys.stdin, search_pattern)\n")
    c.write("for filename, count in data:\n")
    c.indent()
    if suppress_lines:
        c.write("print filename.split(':')[0] + ':' + str(count)\n")
    else:
        c.write("print filename +':' + str(count)\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    frame_file = open("search_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx search_frame.py")
    
def make_identity_frame():
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("import sys\n\n")
    c.write("def read_input(file):\n")
    c.indent()
    c.write("for line in file:\n")
    c.indent()
    c.write("yield line.strip()\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("data = read_input(sys.stdin)\n")
    c.write("for line in data:\n")
    c.indent()
    c.write("if len(line)>0:\n")
    c.indent()
    c.write("print line\n")
    c.dedent()
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    
    frame_file = open("identity_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx identity_frame.py")
    
def sort_numeric(input_file, output_file, ascending=True,num_mappers=None, num_reducers=None):
    '''Use MapReduce to sort a large set of numeric values.'''
    hdfs.copyToHDFS(input_file, input_file.split("/")[-1])
    make_identity_frame()
    if not ascending:
        keycomp ="n"
    else:
        keycomp = "nr"
    hadoop_call = hdmc.build_generic_hadoop_call("identity_frame.py", "identity_frame.py", input_file.split("/")[-1], output_file, [], num_mappers, num_reducers, keycomp)
    print hadoop_call
    hdmc.execute_and_wait(hadoop_call)
    hdfs.copyFromHDFS(output_file, output_file)
    cleanup()
    
def sort_ascii(input_file, output_file, ascending=True,num_mappers=None, num_reducers=None):
    '''Use MapReduce to sort a large set of ASCII values.'''
    hdfs.copyToHDFS(input_file, input_file.split("/")[-1])
    make_identity_frame()
    if ascending:
        keycomp = "r"
        hadoop_call = hdmc.build_generic_hadoop_call("identity_frame.py", "identity_frame.py", input_file.split("/")[-1], output_file, [], num_mappers, num_reducers, keycomp)
    else:
        hadoop_call = hdmc.build_generic_hadoop_call("identity_frame.py", "identity_frame.py", input_file.split("/")[-1], output_file, [], num_mappers, num_reducers)
    print hadoop_call
    hdmc.execute_and_wait(hadoop_call)
    hdfs.copyFromHDFS(output_file, output_file)
    cleanup()
    
def text_search(input_directory, input_files, output_file, search_pattern, suppress_lines=True, num_mappers=None, num_reducers=None):
    '''Use MapReduce to search a collection of input files.'''
    #make an HDFS directory for the input files
    hdfs.mkdir(input_directory)
    for f in input_files:
        hdfs_location = input_directory+"/"+f.split("/")[-1]
        hdfs.copyToHDFS(f, hdfs_location)
        
     #make a special input for the search pattern
    os.system("echo " + search_pattern + " > ziggy_search")
    #make a search frame
    make_grep_frame()
    #make an identity frame
    make_identity_frame()
    #build the hadoop call
    hadoop_call = hdmc.build_generic_hadoop_call("search_frame.py", "identity_frame.py", input_directory, output_file, ["./ziggy_search"], num_mappers, num_reducers)
    hdmc.execute_and_wait(hadoop_call)
    hdfs.copyFromHDFS(output_file, output_file)
    cleanup()
    
def search(input_directory, input_files, output_file, search_pattern, suppress_lines=True, num_mappers=None, num_reducers=None):
    '''Use MapReduce to search a collection of input files.'''
    #make an HDFS directory for the input files
    hdfs.mkdir(input_directory)
    #put the files in that HDFS directory
    for f in input_files:
        #make a temp file with the filename attached
        tmpfile = open(tmp_directory+"/ziggy_search_tmp", "w")
        original_file = open(f)
        for line in original_file:
            print >> tmpfile, f +":"+line
        tmpfile.close()
        original_file.close()
        hdfs_location = input_directory+"/"+f.split("/")[-1]
        hdfs.copyToHDFS(tmp_directory+"/ziggy_search_tmp", hdfs_location)
    os.remove(tmp_directory+"/ziggy_search_tmp")
    #make a special input for the search pattern
    os.system("echo " + search_pattern + " > ziggy_search")
    #make a search frame
    make_search_frame(suppress_lines)
    #make an identity frame
    make_identity_frame()
    #build the hadoop call
    hadoop_call = hdmc.build_generic_hadoop_call("search_frame.py", "identity_frame.py", input_directory, output_file, ["./ziggy_search"], num_mappers, num_reducers)
    hdmc.execute_and_wait(hadoop_call)
    hdfs.copyFromHDFS(output_file, output_file)
    cleanup()
    
def histogram(input_file, output_file, num_mappers=None, num_reducers=None):
    '''Use MapReduce Aggregation to create a Histogram Report from large input file.'''
    hdfs.copyToHDFS(input_file, input_file.split("/")[-1])
    #make histogram mapper
    make_histogram_frame()
    keycomp = "n"
    hadoop_call = hdmc.build_generic_hadoop_call("histogram_frame.py", "aggregate", input_file.split("/")[-1], output_file, [], num_mappers, num_reducers)
    hdmc.execute_and_wait(hadoop_call)
    hdfs.copyFromHDFS(output_file, output_file)
    cleanup()

def cleanup():
    if os.path.isfile("identity_frame.py"):
        os.remove("identity_frame.py")
    if os.path.isfile("histogram_frame.py"):
        os.remove("histogram_frame.py")
    if os.path.isfile("search_frame.py"):
        os.remove("search_frame.py")
    if os.path.isfile("ziggy_search"):
        os.remove("ziggy_search")
    
    
    
    
    