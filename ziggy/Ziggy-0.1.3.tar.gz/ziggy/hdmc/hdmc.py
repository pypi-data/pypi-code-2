'''
Module for running monte carlo and other batch jobs on a Hadoop instance.
The module allows for the submission of scripts (and supporting files)
to a Hadoop MapReduce cluster for batch execution.  Default operation runs
the submitted script for the specified number of iterations on the configured
Hadoop instance.  By supplying an additional reducer script, data generated in
the batch process can be reduced/filtered/processed before it is written to HDFS
and made available to the user.

WARNING: Piped UNIX commands tend to fail when used as mappers and reducers.  Instead
write a BASH or python script.

Created on Jul 28, 2010

@author: dwmclary
'''

import hadoop_config as config
from hdfs import hdfs_access as hdfs
import shlex
import subprocess
import sys
import os
import stat
from code_generator import CodeGenerator
from glob import glob

def make_checkpointing_filter():
    '''Generates a python script which filters checkpointing results from HDMC.'''
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("from copy import copy\n")
    c.write("import sys\n\n")
    c.write("current_key = ''\n")
    c.write("def read_input(file):\n")
    c.indent()
    c.write("global current_key\n")
    c.write("global current_line\n")
    c.write("for line in file:\n")
    c.indent()
    c.write("line = line.strip()\n")
    c.write("try:\n")
    c.indent()
    c.write("key, value = line.split('==HDMC_CHECKPOINT==')\n")
    c.dedent()
    c.write("except ValueError:\n")
    c.indent()
    c.write("key=current_key+'-moredata'\n")
    c.write("value=line\n")
    c.dedent()
    c.write("current_key = key\n")
    c.write("yield key, value\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("global current_key\n")
    c.write("global current_line\n")
    c.write("seen_keys = {}\n")
    c.write("data = read_input(sys.stdin)\n")
    c.write("for key, value in data:\n")
    c.indent()
    c.write("line_data = value.split('==')\n")
    c.write("line_key = int(line_data[1])\n")
    c.write("line_value = line_data[2]\n")
    c.write("if key in seen_keys:\n")
    c.indent()
    c.write("if line_key not in seen_keys[key]:\n")
    c.indent()
    c.write("seen_keys[key][line_key] = line_value\n")
    c.dedent()
    c.dedent()
    c.write("else:\n")
    c.indent()
    c.write("seen_keys[key] = {}\n")
    c.write("seen_keys[key][line_key] = line_value\n")
    c.dedent()
    c.dedent()
    c.write("for key in seen_keys:\n")
    c.indent()
    c.write("lines = seen_keys[key].keys()\n")
    c.write("lines.sort()\n")
    c.write("for l in lines:\n")
    c.indent()
    #c.write("print key +':'+str(l)+':'+seen_keys[key][l]\n")
    c.write("print seen_keys[key][l]\n")
    c.dedent()
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    
    frame_file = open("checkpoint_filter.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx checkpoint_filter.py")
    
    
def make_checkpointing_frame(script, checkpoint_names, checkpoint_dir,arguments="", files = True, debug=False):
    '''Generates a python script which given a list of files to be processed, 
executes the specified script in over the files in parallel via MapReduce.'''

    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("from glob import glob\n")
    c.write("import sys, os, subprocess, shlex, random, time, re\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("wait_counter = 1\n")
    c.write("time.sleep(random.random())\n")
    #choose a checkpoint
    c.write("all_checkpoints = "+str(checkpoint_names)+"\n")
    c.write("this_checkpoint = random.choice(all_checkpoints)\n")
    c.write("this_checkpoint_start = this_checkpoint+'_start'\n")
    c.write("this_checkpoint_end = this_checkpoint+'_end'\n")
    c.write("current_checkpoints = glob('"+checkpoint_dir+"/*')\n")
    c.write("final_checkpoints = glob('"+checkpoint_dir+"/*_end')\n")
    c.write("while len(final_checkpoints) < len(all_checkpoints):\n")
    c.indent()
    c.write("for i in range(len(current_checkpoints)):\n")
    c.indent()
    c.write("current_checkpoints[i] = re.sub('"+checkpoint_dir+"/', '', current_checkpoints[i])\n")
    c.dedent()
    c.write("while this_checkpoint_end in current_checkpoints:\n")
    c.indent()
    c.write("this_checkpoint = random.choice(all_checkpoints)\n")
    c.write("this_checkpoint_start = this_checkpoint+'_start'\n")
    c.write("this_checkpoint_end = this_checkpoint+'_end'\n")
    c.write("current_checkpoints = glob('"+checkpoint_dir+"/*')\n")
    c.write("final_checkpoints = glob('"+checkpoint_dir+"/*_end')\n")
    c.write("for i in range(len(current_checkpoints)):\n")
    c.indent()
    c.write("current_checkpoints[i] = re.sub('"+checkpoint_dir+"/', '', current_checkpoints[i])\n")
    c.dedent()
    c.write("if len(final_checkpoints) == len(all_checkpoints):\n")
    c.indent()
    c.write("exit()\n")
    c.dedent()
    c.dedent()
    c.write("\n")
    c.write("subprocess.call(['touch','"+checkpoint_dir+"'+'/'+this_checkpoint+'_start'])\n")
    c.write("subprocess.call(['chmod','777','"+checkpoint_dir+"'+'/'+this_checkpoint+'_start'])\n")
    cmd = str(shlex.split("./"+script.split("/")[-1] + " " + arguments))
    c.write("os.system('chmod a+rwx "+script.split("/")[-1]+"')\n")
    if files:
        c.write("cmd = "+cmd+"+['./'+this_checkpoint]\n")
    else:
        c.write("argf = open('./'+this_checkpoint).readlines()\n")
        c.write("for i in range(len(argf)):\n")
        c.indent()
        c.write("argf[i] = argf[i].strip()\n")
        c.dedent()
        
        c.write("cmd = "+cmd+"+argf\n")
        
    c.write("p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n")
    c.write("output, error = p.communicate()\n")
    c.write("sts = p.wait()\n")
    if not debug:
        c.write("output = output.strip()\n")
        c.write("if len(output) > 0:\n")
        c.indent()
        c.write("line_count = 0\n")
        c.write("newline = '\\n'\n")
        c.write("for line in output.split(newline):\n")
        c.indent()
        c.write("print this_checkpoint+'==HDMC_CHECKPOINT==LINE=='+ str(line_count) + '=='+line.strip()\n")
        c.write("line_count += 1\n")
        c.dedent()
        c.dedent()
        c.write("if len(error.strip()) > 0:\n")
        c.indent()
        c.write("print >> sys.stderr, error.strip()\n")
        c.write("os.system('rm "+checkpoint_dir+"'+'/'+this_checkpoint)\n")
        c.write("exit(1)\n")
        c.dedent()
        c.write("else:\n")
        c.indent()
        c.write("subprocess.call(['touch','"+checkpoint_dir+"'+'/'+this_checkpoint+'_end'])\n")
        c.write("subprocess.call(['chmod','777','"+checkpoint_dir+"'+'/'+this_checkpoint+'_end'])\n")
        c.dedent()
        c.write("os.system('rm "+checkpoint_dir+"/'+this_checkpoint+'_start')\n")
    else:
        c.write("print output.strip(),error.strip()\n")
    c.write("subprocess.call(['touch','"+checkpoint_dir+"'+'/'+this_checkpoint+'_end'])\n")

    c.write("this_checkpoint = random.choice(all_checkpoints)\n")
    c.write("current_checkpoints = glob('"+checkpoint_dir+"/*')\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    
    frame_file = open("checkpoint_frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx checkpoint_frame.py")
    if not files:
        os.system("cp checkpoint_frame.py checkpoint_frame_save.py")
    
def make_frame(script, arguments="", iterations=1, debug=False):
    '''Generates a basic python frame for running a batch job on a MapReduce cluster.'''
    cmd = str(shlex.split("./"+script.split("/")[-1] + " " + arguments))
    c = CodeGenerator()
    c.begin()
    c.write("#! /usr/bin/env python\n\n")
    c.write("import sys, os, subprocess, shlex, random\n\n")
    c.write("def main():\n")
    c.indent()
    c.write("os.system('chmod a+rwx "+script.split("/")[-1]+"')\n")
    c.write("for i in range("+str(iterations/config.num_map_tasks)+"):\n")
    c.indent()
    c.write("p = subprocess.Popen("+cmd+", stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n")
    c.write("output, error = p.communicate()\n")
    c.write("sts = p.wait()\n")
    if not debug:
        c.write("print output\n")
    else:
        c.write("print output,error\n")
    c.dedent()
    c.dedent()
    c.write("\n\n")
    c.write('if __name__ == \"__main__\":\n')
    c.indent()
    c.write("main()\n")
    c.write("\n")
    
    frame_file = open("frame.py", "w")
    print >> frame_file, c.end()
    frame_file.close()
    os.system("chmod a+rwx frame.py")
    
def get_output_hdfs_name(output_data_name):
    '''Given the full path to a file or directory, returns its HDFS equivalent'''
    output_path = output_data_name.split("/")
    return output_path[len(output_path)-1]


def build_hadoop_call(script, output_data_name, iterations=1, supporting_file_list = None, reduction_script=None, arguments=None, debug=False, num_mappers=None, num_reducers=None):
    '''Builds a call array suitable for subprocess.Popen which submits a streaming job to 
the configured MapReduce instance.  The function also generates the necessary execution frame.'''
    # I/O setup
    hadoop_call = [config.hadoop, 'jar', config.hadoop_streaming]
    if num_mappers:    
        hadoop_call += ["-D", "mapred.map.tasks="+str(num_mappers)]
    if num_reducers:
        hadoop_call += ["-D", "mapred.reduce.tasks="+str(num_reducers)]
        
    
    hadoop_call += ['-input', 'dummy', '-output', get_output_hdfs_name(output_data_name)]
    #mapper name
    hadoop_call += ['-mapper', "frame.py"]
    
    #set the reducer
    if reduction_script:
        hadoop_call += ['-reducer', get_output_hdfs_name(reduction_script)]
    else:
        hadoop_call += ['-reducer', 'NONE']
        
    #build the supporting file list
    file_list = ["-file", script]
    file_list += ["-file", "./frame.py"]
    if reduction_script:
        file_list += ["-file", reduction_script]
    if supporting_file_list:
        for f in supporting_file_list:
            file_list += ["-file", f]
            
    hadoop_call += file_list
    make_frame(script, arguments, iterations, debug)
    return hadoop_call

def build_checkpoint_call(script, output_data_name, supporting_file_list, reduction_script=None, arguments=None, num_mappers=None, num_reducers=None):
    '''Builds a call array suitable for subprocess.Popen which submits a streaming job to 
     the configured MapReduce instance.  The function also generates the necessary execution frame.'''
    # I/O setup
    hadoop_call = [config.hadoop, 'jar', config.hadoop_streaming]
    if num_mappers:    
        hadoop_call += ["-D", "mapred.map.tasks="+str(num_mappers)]
        
    if num_reducers:
        hadoop_call += ["-D", "mapred.reduce.tasks="+str(num_reducers)]
        
    hadoop_call += ['-input', 'dummy', '-output', get_output_hdfs_name(output_data_name)]
    #mapper name
    hadoop_call += ['-mapper', "checkpoint_frame.py"]
    
    #set the reducer
    if reduction_script:
        hadoop_call += ['-reducer', get_output_hdfs_name(reduction_script)]
    else:
        hadoop_call += ['-reducer', 'NONE']
        
    #build the supporting file list
    file_list = ["-file", script]
    file_list += ["-file", "./checkpoint_frame.py"]
    if reduction_script:
        if reduction_script != "NONE":
            file_list += ["-file", reduction_script]
    if supporting_file_list:
        for f in supporting_file_list:
            file_list += ["-file", f]
            
    hadoop_call += file_list
    return hadoop_call
    

def build_generic_hadoop_call(mapper, reducer, input, output, supporting_file_list = None, num_mappers = None, num_reducers = None, key_comparator=None):
    '''Builds a call array suitable for subprocess.Popen which submits a streaming job to 
the configured MapReduce instance.'''
     # I/O setup
    hadoop_call = [config.hadoop, 'jar', config.hadoop_streaming]
                   
    
  #process mapper, reducer, and key comparator options
   
    if num_mappers:
        hadoop_call += ["-D", "mapred.map.tasks="+str(num_mappers)]
    if num_reducers:
        hadoop_call += ["-D", "mapred.reduce.tasks="+str(num_reducers)]
    if key_comparator:
        hadoop_call += ["-D", "mapreduce.partition.keycomparator.options="+key_comparator]
        
    hadoop_call += ['-input', input, '-output', output]
        
     #set mapper and reducer
    hadoop_call += ['-mapper', mapper]    
    if reducer != "NONE":
        hadoop_call += ['-reducer', reducer]
    else:
        hadoop_call += ['-reducer', 'NONE']
    
    #build the supporting file list
    if reducer not in ["NONE", "aggregate"]:
        file_list = ["-file", mapper, "-file", reducer]
    else:
        file_list = ["-file", mapper]
    
    if supporting_file_list:
        for f in supporting_file_list:
            file_list += ["-file", f]
    
    hadoop_call += file_list
    return hadoop_call


def execute(hadoop_call):
    '''Nonblocking execution of the given call array'''
    p = subprocess.Popen(hadoop_call)

def execute_and_wait(hadoop_call):
    '''Blocking execution of the given call array'''
    p = subprocess.Popen(hadoop_call)
    sts = p.wait()
    return sts

  
def create_dummy_data():
    '''Creates a piece of dummy map input data in HDFS.  This is necessary because 
Hadoop streamingrequires input for mapping tasks.'''  
    f = open("dummy", "w")
    print >> f, "dummy data"
    f.close()
    hdfs.copyToHDFS("dummy", "dummy")

 
def load_data_to_hfds(input_data_file):
    '''Loads a data file to HDFS.  For future use.'''   
    input_path = input_data_file.split("/")
    hdfs_filename = input_path[len(input_path)-1]
    hdfs.copyToHDFS(input_data_file, hdfs_filename)

def download_hdfs_data(output_data_name):
    '''Given a full path, downloads an output directory from HDFS to the specified location.'''    
    output_path = output_data_name.split("/")
    hdfs_filename = output_path[-1]
    f = open(output_data_name, "w")
    print >> f, hdfs.cat(hdfs_filename+"/part*")["stdout"]
    f.close()

def print_hdfs_data(output_data_name):
    '''Given a full path, prints the output of all parts of an HDFS directory.'''
    output_path = output_data_name.split("/")
    hdfs_filename = output_path[-1]
    print hdfs.cat(hdfs_filename+"/part*")["stdout"]


def set_checkpoint_directory(output_data_name):
    '''Creates a checkpoint directory for parallel file processing.  This directory
is always named hdmc_checkpoints and exists at the same level as the trailing entry
in output_data_name.'''    
    output_path = output_data_name.split("/")
    output_path.pop()
    output_dir = config.shared_tmp_space+"/"+os.getlogin()
    print output_dir
    try:
        os.mkdir(output_dir)
        os.system('chmod 777 '+ output_dir)
    except OSError:
        pass
    cwd = os.getcwd()
    os.chdir(output_dir)
    os.system("rm -rf hdmc_checkpoints")
    os.system("mkdir hdmc_checkpoints")
    os.system("chmod 777 hdmc_checkpoints")
    os.chdir(cwd)
    return output_dir+"/hdmc_checkpoints"

def get_checkpoint_names(file_list):
    '''Given a list of file or command names, produces checkpoint names by taking
    the last member of the array generated by splitting in /'''
    checkpoints = []
    for f in file_list:
        if "/" in f:
            path = f.split("/")
            checkpoints.append(path[-1])
        else:
            path=f
            checkpoints.append(f)
    return checkpoints

def make_pseudo_checkpoints(file_list):
    '''Designed to make checkpointing long lists of parameters (e.g. URLs) easier'''
    checkpoints = []
    os.system('mkdir pseudo_checkpoints')
    cp_count = 0
    for f in file_list:
        os.system('echo '+f + "> pseudo_checkpoints/" + str(cp_count))
        checkpoints.append(str(cp_count))
        file_list[cp_count] = "pseudo_checkpoints/" + str(cp_count)
        cp_count += 1
    return checkpoints
    


def submit(script, output_data_name, iterations=1, supporting_file_list = None, reduction_script=None, arguments="", debug=False, num_mappers=None, num_reducers=None):
    '''Submits script non-blocking job to a MapReduce cluster and collects output
in output_data_name.  Supporting filenames can be passed
as a list, as can a reducing/filtering script.  Arguments to the submitted script
should be passed as a string.'''    
    create_dummy_data()
    hadoop_call = build_hadoop_call(script, output_data_name, iterations, supporting_file_list, reduction_script, arguments, debug, num_mappers, num_reducers)
    execute(hadoop_call)
    


def submit_inline(script, output_data_name, iterations=1, supporting_file_list = None, reduction_script=None, arguments="", debug=False, num_mappers=None, num_reducers=None):
    '''Submits script blocking job to a MapReduce cluster and collects output
in output_data_name.  Supporting filenames can be passed
as a list, as can a reducing/filtering script.  Arguments to the submitted script
should be passed as a string.'''      
    create_dummy_data()
    hadoop_call = build_hadoop_call(script, output_data_name, iterations, supporting_file_list, reduction_script, arguments, debug, num_mappers, num_reducers)
    execute_and_wait(hadoop_call)
    download_hdfs_data(output_data_name)
    cleanup()
    
def submit_checkpoint_inline(script, output_data_name, file_list, supporting_file_list=[], reduction_script = None, arguments="", files=True, debug=False, num_mappers=None, num_reducers=None):
    '''Submits a script to a MapReduce cluster for 
    parallel operation on a number of files.  An optional reducer script can be 
    applied as well, but should filter the map results by splitting file output
    on ===HDMC_CHECKPOINT===. Arguments to the submitted script
    should be passed as a string. Blocking.'''  
    create_dummy_data()
    checkpoint_dir = set_checkpoint_directory(output_data_name)
    if files:
        checkpoints = get_checkpoint_names(file_list)
    else:
        print "not processing files"
        checkpoints = make_pseudo_checkpoints(file_list)
        
    make_checkpointing_frame(script, checkpoints, checkpoint_dir, arguments, files, debug)
    if not reduction_script:
        reduction_script = "checkpoint_filter.py"
        make_checkpointing_filter()
#    elif not files:
#        reduction_script = "NONE"
        
    hadoop_call = build_checkpoint_call(script, output_data_name, file_list+supporting_file_list, reduction_script, arguments, num_mappers, num_reducers)
    
    print "executing"
    execute_and_wait(hadoop_call)
    download_hdfs_data(output_data_name)
    cleanup()
    return checkpoints

def submit_checkpoint(script, output_data_name, file_list, supporting_file_list=[], reduction_script = None, arguments="", files=True, debug=False, num_mappers=None, num_reducers=None):
    '''Submits a script to a MapReduce cluster for 
    parallel operation on a number of files.  An optional reducer script can be 
    applied as well, but should filter the map results by splitting file output
    on ===HDMC_CHECKPOINT===. Arguments to the submitted script
    should be passed as a string.  Non-blocking.'''  
    create_dummy_data()
    checkpoint_dir = set_checkpoint_directory(output_data_name)
    if files:
        checkpoints = get_checkpoint_names(file_list)
    else:
        print "not processing files"
        checkpoints = make_pseudo_checkpoints(file_list)
        
    make_checkpointing_frame(script, checkpoints, checkpoint_dir, arguments, files, debug)
    if not reduction_script:
        reduction_script = "checkpoint_filter.py"
        make_checkpointing_filter()
#    elif not files:
#        reduction_script = "NONE"
        
    hadoop_call = build_checkpoint_call(script, output_data_name, file_list+supporting_file_list, reduction_script, arguments, num_mappers, num_reducers)
    
    print "executing"
    execute_and_wait(hadoop_call)
    download_hdfs_data(output_data_name)
    cleanup()
    return checkpoints
    
def cleanup():
    '''Remove files generated by HDMC.''' 
    if os.path.isfile("frame.py"):
        os.remove("frame.py")
    if os.path.isfile("checkpoint_frame.py"):
        os.remove("checkpoint_frame.py")
    if os.path.isfile("checkpoint_filter.py"):
        os.remove("checkpoint_filter.py")
    if os.path.isfile("dummy"):
        os.remove("dummy")
    if os.path.isdir("pseudo_checkpoints"):
        pcps = glob("pseudo_checkpoints/*")
        for f in pcps:
            os.remove(f)
        os.removedirs("pseudo_checkpoints")
    
    
