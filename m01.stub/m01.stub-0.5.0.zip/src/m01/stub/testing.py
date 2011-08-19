###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import os.path
import zipfile
import sys
import shutil
import fnmatch
import time
import tempfile
import urllib
import subprocess
import platform
import setuptools.archive_util

mongoProcess = None

# helper for zip and unzip mongodb for simpler sample data setup
def zipFolder(folderPath, zipPath, topLevel=False):
    """Zip a given folder to a zip file, topLevel stores top elvel folder too"""
    # remove existing zip file
    if os.path.exists(zipPath):
        os.remove(zipPath)
    zip = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
    path = os.path.normpath(folderPath)
    # os.walk visits every subdirectory, returning a 3-tuple of directory name,
    # subdirectories in it, and filenames in it
    for dirPath, dirNames, fileNames in os.walk(path):
        # walk over every filename
        for file in fileNames:
            # ignore hidden files
            if not file.endswith('.lock'):
                if topLevel:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath, file)[len(path)+len(os.sep):]
                    arcName = os.path.join(os.path.basename(path), relPath)
                    zip.write(fPath, arcName)
                else:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath[len(path):], file)
                    zip.write(fPath, relPath) 
    zip.close()
    return None


def unZipFile(zipPath, target):
    # If the output location does not yet exist, create it
    if not os.path.isdir(target):
        os.makedirs(target)    
    zip = zipfile.ZipFile(zipPath, 'r')
    for each in zip.namelist():
        # check to see if the item was written to the zip file with an
        # archive name that includes a parent directory. If it does, create
        # the parent folder in the output workspace and then write the file,
        # otherwise, just write the file to the workspace.
        if not each.endswith('/'): 
            root, name = os.path.split(each)
            directory = os.path.normpath(os.path.join(target, root))
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file(os.path.join(directory, name), 'wb').write(zip.read(each))
    zip.close()


# support missing ignore pattern in py25
def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns


def copytree(src, dst, ignore=None):
    """Recursively copy a directory tree using copy2()"""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors


def startMongoDBServer(host='localhost', port=45017, options=None,
    sandBoxDir=None, dataDir=None, logDir=None, dataSource=None, sleep=2.0,
    dataSourceCopyTreeIgnorePatterns='*.svn', downloadURL=None):
    """Start the mongodb test server.
    
    NOTE: there is one important thing. You allways need to make sure that you
    use a new connection in each test using this setup. Otherwise a new test 
    will reuse a connection from a previous connection pool setup. (pymongo)
    """

    # setup server folder
    if sandBoxDir is None:
        here = os.path.dirname(__file__)
        sandbox = os.path.join(here, 'sandbox')
    else:
        sandbox = sandBoxDir

    # setup data dir
    if dataDir is None:
        data = os.path.join(sandbox, 'data')
    else:
        data = dataDir

    # setup logs dir
    if logDir is None:
        logs = os.path.join(sandbox, 'logs')
    else:
        logs = logDir

    # setup sandbox folder
    if not os.path.exists(sandbox):
        os.mkdir(sandbox)

    # download and install a server
    if not 'bin' in os.listdir(sandbox):
        arch = platform.architecture()[0]
        # explicit download url
        if downloadURL:
            url = downloadURL
        # windows
        elif os.name == 'nt' and arch == '32bit':
            url = 'http://downloads.mongodb.org/win32/mongodb-win32-i386-1.8.2.zip'
        elif os.name == 'nt' and arch == '64bit':
            url = 'http://downloads.mongodb.org/win32/mongodb-win32-x86_64-1.8.2.zip'
        # mac
        elif os.name == 'mac' and arch == '32bit':
            url = 'http://fastdl.mongodb.org/osx/mongodb-osx-i386-1.8.2.tgz'
        elif os.name == 'mac' and arch == '64bit':
            url = 'http://fastdl.mongodb.org/osx/mongodb-osx-x86_64-1.8.2.tgz'
        # posix
        elif os.name == 'posix' and arch == '64bit':
            url = 'http://fastdl.mongodb.org/linux/mongodb-linux-i686-1.8.2.tgz'
        elif os.name == 'posix' and arch == '64bit':
            url = 'http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-1.8.2.tgz'
        else:
            raise ValueError("No download found, define a downloadURL")

        tmpDir = tempfile.mkdtemp('m01-stub-download-tmp')
        handle, downloadFile = tempfile.mkstemp(prefix='m01-stub-download')
        urllib.urlretrieve(url, downloadFile)
        setuptools.archive_util.unpack_archive(downloadFile, tmpDir)
        topLevelDir = os.path.join(tmpDir, os.listdir(tmpDir)[0])
        for fName in os.listdir(topLevelDir):
            source = os.path.join(topLevelDir, fName)
            dest = os.path.join(sandbox, fName)
            shutil.move(source, dest)

    # first remove the original data folder, we need an empty setup
    if os.path.exists(data):
        try:
            shutil.rmtree(data)
        except Exception, e:
            # this was to early just try again
            time.sleep(sleep)
            shutil.rmtree(data)

    # re-use predefined mongodb data for simpler testing
    if dataSource is not None and os.path.exists(dataSource):
        if dataSource.endswith('.zip'):
            # extract zip file to dataDir
            try:
                unZipFile(dataSource, data)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleep)
                if os.path.exists(data):
                    shutil.rmtree(data)
                unZipFile(dataSource, data)
        else:
            # copy source folder to dataDir
            ignore = None
            if dataSourceCopyTreeIgnorePatterns is not None:
                ignore = ignore_patterns(dataSourceCopyTreeIgnorePatterns)
            try:
                copytree(dataSource, data, ignore=ignore)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleep)
                if os.path.exists(data):
                    shutil.rmtree(data)
                copytree(dataSource, data, ignore=ignore)

    # ensure new data location if not created with dataSource
    if not os.path.exists(data):
        try:
            os.mkdir(data)
        except Exception, e:
            # this was to early just try again
            time.sleep(sleep)
            os.mkdir(data)

    # start the mongodb stub server
    if os.name == 'nt':
        cmd = os.path.join(sandbox, 'bin', 'mongod.exe')
    else:
        cmd = os.path.join(sandbox, 'bin', 'mongod')

    if options is None:
        cmd = '%s --nohttpinterface --nssize 100 --dbpath "%s"' % (cmd, data)
    else:
        cmd = '%s %s --dbpath "%s"' % (cmd, options, data)

    # setup log dir
    if '--logpath' not in cmd:
        if not os.path.exists(logs):
            os.mkdir(logs)
        cmd += ' --logpath %s' % os.path.join(logs, 'm01-stub.log')
    # set host
    if host != 'localhost':
        cmd += ' --bind_ip %s' % host
    # set port
    if port != 27017:
        cmd += ' --port %s' % port

    # append run cmd
    cmd += ' run'

    # start mongodb server
    try:
        p = subprocess.Popen(cmd, shell=False)
    except Exception, e:
        raise Exception("Subprocess error: %s" % e)

    global mongoProcess
    mongoProcess = p

    # give some second for start the mongodb server
    time.sleep(sleep)


def stopMongoDBServer(sleep=1.0):
    global mongoProcess
    # kill mongodb by it's pid. Note, we don't care about the database.
    # Let me know if you know a better kill method
    if os.name == 'nt':
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(1, False,
            mongoProcess.pid)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)
    else:
        import signal
        os.kill(int(mongoProcess.pid), signal.SIGTERM)

    mongoProcess = None
    # give a second for stop the mongodb server
    time.sleep(sleep)


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    # setup mongodb server
    startMongoDBServer()


def doctestTearDown(test):
    # tear down mogodb server
    stopMongoDBServer()
