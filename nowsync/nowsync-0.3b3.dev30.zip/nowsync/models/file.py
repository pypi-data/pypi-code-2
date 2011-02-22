from __future__ import with_statement
import os
import hashlib
import fnmatch

from nowsync.utils import relpath

def is_under_dir(path, dir):
    """Determine is a path under a directory
    
    """
    path = os.path.realpath(path)
    dir = os.path.realpath(dir)
    head = path
    tail = True
    while tail:
        if head == dir:
            return True
        head, tail = os.path.split(head)
    return False

def cal_signature(path):
    """Calculate signature of a file
    
    """
    with open(path, 'rb') as file:
        content = file.read()
    hash = hashlib.sha1(content)
    return hash.hexdigest()

def match_patterns(path, patterns):
    """Is a path matches file patterns
    
    """
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def get_files(folder, allows=None, ignores=None):
    """Get file map in a folder with signature
    
    """
    if allows is None:
        allows = None
    if ignores is None:
        ignores = []
    file_map = {}
    for root, _, files in os.walk(unicode(folder)):
        for filepath in files:
            path = os.path.join(root, filepath)
            path = relpath(path, folder)
            if match_patterns(path, ignores):
                continue
            if not match_patterns(path, allows):
                continue
            if not os.path.isfile(path):
                continue
            sig = cal_signature(path)
            file_map[path.replace('\\', '/')] = sig
    return file_map