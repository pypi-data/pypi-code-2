# Copyright (c) 2011 Zhigang Wang <zhigang.x.wang@oracle.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Porting of twisted.python.zipstream to tarfile.
"""

import tarfile
import os.path


def count_chunks(filename, chunksize=4096):
    """
    Predict the number of chunks that will be extracted from the entire
    tarfile, given chunksize blocks.
    """
    totalchunks = 0
    tf = tarfile.open(filename)
    for tarinfo in tf:
        count, extra = divmod(tarinfo.size, chunksize)
        if extra > 0:
            count += 1
        totalchunks += count or 1
    return totalchunks


def extract_chunky(filename, directory='.', chunksize=4096):
    """
    Return a generator for the tarfile. This implementation will yield after
    every chunksize uncompressed bytes, or at the end of a file, whichever
    comes first.

    The value it yields is the number of chunks left to untar.
    """
    tf = tarfile.open(filename)
    remaining = count_chunks(filename, chunksize)
    for tarinfo in tf:
        if tarinfo.isfile():
            targetpath = os.path.join(directory, tarinfo.name)
            if targetpath[-1:] == '/':
                targetpath = targetpath[:-1]
            targetpath = os.path.normpath(targetpath)

            upperdirs = os.path.dirname(targetpath)
            if upperdirs and not os.path.exists(upperdirs):
                os.makedirs(upperdirs)

            outfile = open(targetpath, 'wb')
            fp = tf.extractfile(tarinfo)
            if tarinfo.size == 0:
                remaining -= 1
                yield remaining
            while fp.tell() < tarinfo.size:
                hunk = fp.read(chunksize)
                outfile.write(hunk)
                remaining -= 1
                yield remaining
            outfile.close()
        else:
            tf.extract(tarinfo, directory)
            remaining -= 1
            yield remaining
