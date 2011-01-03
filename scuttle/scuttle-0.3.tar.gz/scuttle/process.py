#!/usr/bin/env python

from __future__ import with_statement

import base64
import datetime
import gzip
import os
import sys
import time
import uuid
from contextlib import closing

def unique():
    value = uuid.uuid4().bytes
    return base64.b64encode(value, ('-', '_')).rstrip('=')


from httplib import BadStatusLine
from boto.exception import S3ResponseError
from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.s3.key import Key
class S3Uploader(object):
    def __init__(self, aws_key, aws_secret_key):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.conn = S3Connection(self.aws_key, self.aws_secret_key)

    def retry(self, func, *args, **kwargs):
        """retry all commands a few times func because S3 occasionally returns 500 errors"""

        retry_sleep = 0.2
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except (S3ResponseError, BadStatusLine, ValueError), exc:
                # ValueError is raised when httplib doesn't handle an invalid response properly
                # "ValueError: invalid literal for int() with base 16: ''"

                if not isinstance(exc, (BadStatusLine, ValueError)) and exc.status != 500:
                    raise

                last_error = exc
                time.sleep(retry_sleep)
                retry_sleep *= 2

        raise last_error

    def upload(self, filename, bucket, key_name, metadata=None):
        bucket = Bucket(self.conn, bucket)
        key = Key(bucket, key_name)
        key.content_type = "application/x-gzip"
        if metadata:
            for k, v in metadata.items():
                key.set_metadata(k, str(v))
        with open(filename, "rb") as fp:
            self.retry(key.set_contents_from_file, fp)
            # self.retry(key.set_acl, '')
        # Verify it exists (might need to wait a bit before it shows up)
        # success = bool(self.retry(bucket.lookup, key_name))

class ProcessLogs(object):
    def __init__(self, input_path, aws_key, aws_secret_key, aws_bucket):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_bucket = aws_bucket
        self.input_path = input_path
        self.input_files = [f for f in os.listdir(input_path) if f.endswith('.log')]
        self.input_files.sort()
        self.output_files = {}
        self.output_files_list = []
        self.max_output_files = None
        self.max_file_size = 128*1024*1024
        self.output_path = os.path.join(self.input_path, "processed")
        self.working_path = os.path.join(self.input_path, "working")
        self.trash_path = os.path.join(self.input_path, "trash")
        for path in (self.output_path, self.working_path, self.trash_path):
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError, exc:
                    if exc.errno != 17: # If the error isn't "file exists" then reraise
                        raise
    
    def close_all_output_files(self):
        for base_filename, fp in self.output_files.itervalues():
            fp.close()
        self.output_files = {}
    
    def get_output_file(self, event, timestamp):
        date = datetime.datetime.utcfromtimestamp(timestamp)
        base_filename = "%s/%s/%s-" % (event, date.strftime("%Y-%m-%d"), date.strftime("%H"))
        
        if base_filename in self.output_files:
            return self.output_files[base_filename]
        
        if self.max_output_files and len(self.output_files_list) > self.max_output_files:
            t = self.output_files_list.pop()
            fp = self.output_files.pop(t)[1]
            fp.close()
        
        base_name = os.path.join(self.output_path, base_filename)
        
        base_path = base_name.rsplit('/', 1)[0]
        if not os.path.exists(base_path):
            try:
                os.makedirs(base_path)
            except OSError, exc:
                if exc.errno != 17: # If the error isn't "file exists" then reraise
                    raise
        
        filename = base_name + ("%d-%s.log" % (timestamp, unique()))
        fp = open(filename, "a")
        self.output_files[base_filename] = (base_filename, fp)
        self.output_files_list.insert(0, base_filename)
        
        return base_filename, fp
    
    def write_event(self, event, timestamp, data):
        base_filename, fp = self.get_output_file(event, timestamp)
        fp.write(data+"\n")
        if fp.tell() > self.max_file_size - 1024:
            fp.close()
            del self.output_files[base_filename]
    
    def process_file(self, filename, path):
        working_filename = os.path.join(self.working_path, filename)
        os.rename(path, working_filename)
        time.sleep(2) # Incase someone's writing to the file give them time to notice
        with open(working_filename, "r") as fp:
            for line_num, line in enumerate(fp):
                line = line.strip()
                try:
                    timestamp, event, data = line.split('\t', 2)
                except ValueError:
                    sys.stderr.write("Failed line %d in file %s: %s\n" % (line_num, filename, repr(line)))
                    continue
                if '.' in timestamp:
                    timestamp = float(timestamp)
                else:
                    timestamp = int(timestamp)
                self.write_event(event, timestamp, data)
        os.rename(working_filename, os.path.join(self.trash_path, filename))
    
    def empty_trash(self, max_age=3*24*60*60):
        now = time.time()
        for fname in os.listdir(self.trash_path):
            path = os.path.join(self.trash_path, fname)
            st = os.stat(path)
            if now - st.st_ctime > max_age:
                os.unlink(path)
    
    def run(self):
        for filename in self.input_files:
            path = os.path.join(self.input_path, filename)
            if os.path.isfile(path):
                self.process_file(filename, path)
        self.close_all_output_files()
        
        s3_uploader = S3Uploader(self.aws_key, self.aws_secret_key)
        
        for root, dirs, files in os.walk(self.output_path):
            to_remove = []
            for d in dirs:
                full = os.path.join(root, d)
                if d[0] == '.':
                    to_remove.append(d)
            for d in to_remove:
                dirs.remove(d)
            
            files.sort()
            for filename in files:
                if filename[0] == '.':
                    continue
                path = os.path.join(root, filename)
                
                if not filename.endswith(".gz") and os.path.getsize(path) > 512:
                    gzip_name = path+".gz"
                    with open(path, "rb") as infp:
                        with closing(gzip.open(gzip_name, "wb")) as outfp:
                            while True:
                                block = infp.read(1024*128)
                                if not block:
                                    break
                                outfp.write(block)
                    os.unlink(path)
                else:
                    gzip_name = path
                
                key = gzip_name[len(self.output_path)+1:]
                s3_uploader.upload(gzip_name, self.aws_bucket, key)
                os.unlink(gzip_name)

        self.empty_trash()

if __name__ == "__main__":
    input_path = sys.argv[1]
    aws_key = sys.argv[2]
    aws_secret_key = sys.argv[3]
    aws_bucket = sys.argv[4]
    ProcessLogs(input_path, aws_key, aws_secret_key, aws_bucket).run()
