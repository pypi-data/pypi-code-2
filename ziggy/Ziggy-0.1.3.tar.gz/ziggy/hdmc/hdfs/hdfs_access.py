'''
Created on May 17, 2010

@author: dwmclary
'''

from . import hdfs_config as config
import subprocess


def run(args):
    '''Generic runner for HDFS access'''
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    r = p.communicate()
    result = {"stdout":r[0], "stderr":r[1]}
    return result


def cat(filename):
    '''Runs HDFS cat on a filename or glob passed as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-cat", filename]
    return run(args)


def ls(filename):
    '''Runs HDFS ls on a directory or glob passed as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-ls", filename]
    return run(args)

def tail(filename):
    args = [config.hadoop, "dfs", "-tail", filename]
    return run(args)

def mv(filename1, filename2):
    args = [config.hadoop, "dfs", "-mv", filename1, filename2]
    return run(args)

def rm(filename):
    '''Runs HDFS rmr on a filename or glob passed as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-rmr", filename]
    return run(args)

def delete(filename):
    '''Runs HDFS rmr on a filename or glob passed as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-rm", filename]
    return run(args)

def mkdir(dirname):
    '''Runs HDFS mkdir on a directory name as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-mkdir", dirname]
    return run(args)

def get_merge(pattern, dst):
    '''Runs HDFS rmr on a filename or glob passed as a string
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-getmerge", pattern, dst]
    return run(args)

def mv(src, dst):
    '''Runs HDFS mv: move src HDFS file to dst
    Returns the result as a string read from STOUT'''
    args = [config.hadoop, "dfs", "-mv", src, dst]
    return run(args)



def copyToHDFS(filename, hdfs_filename):
    args = [config.hadoop, "dfs", "-put", filename, hdfs_filename]
    return run(args)

def copyFromHDFS(hdfs_filename, filename):
    args = [config.hadoop, "dfs", "-get", hdfs_filename, filename]
    return run(args)
    