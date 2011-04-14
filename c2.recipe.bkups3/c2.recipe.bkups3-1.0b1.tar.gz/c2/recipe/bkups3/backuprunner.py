#!/usr/bin/env python
# encoding: utf-8
"""
backuprunner.py

Created by Manabu Terada on 2011-04-13.
Copyright (c) 2011 CMScom. All rights reserved.
"""

import sys
import os
import tarfile
from DateTime import DateTime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import logging

logger = logging.getLogger('bkups3')


def quote_command(command):
    # Quote the program name, so it works even if it contains spaces
    command = " ".join(['"%s"' % x for x in command])
    if sys.platform[:3].lower() == 'win':
        # odd, but true: the windows cmd processor can't handle more than
        # one quoted item per string unless you add quotes around the
        # whole line.
        command = '"%s"' % command
    return command


def make_tar(folder_path, tar_name):
     arcname = os.path.basename(folder_path)
     out = tarfile.TarFile.open(tar_name, 'w:gz')
     out.add(folder_path, arcname)
     out.close()
     return tar_name

def _get_file_time(dirname, filename):
    return DateTime(os.path.getmtime(os.path.join(dirname,filename)))

S3_FILES_FOLDER = 'files'
S3_BLOBS_FOLDER = 'blobs'
S3_BLOBS_FILENAME = 'blob.tar.gz'
def send_s3(aws_id, aws_key, bucket_name, backup_location, blob_bk_filename):
    send_files = []
    conn = S3Connection(aws_id, aws_key)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)

    # files
    rs = dict((key.name, key.last_modified) for key in bucket.list(S3_FILES_FOLDER))
    files = os.listdir(backup_location)
    for filename in files:
        if filename.startswith('.'):
            continue
        full_filename = '/'.join((S3_FILES_FOLDER, filename))
        if full_filename in rs:
            if _get_file_time(backup_location, filename) > DateTime(rs[full_filename]):
                f = os.path.join(backup_location, filename)
                k.key = full_filename
                k.set_contents_from_filename(f)
                send_files.append(k.key)
        else:
            f = os.path.join(backup_location, filename)
            k.key = '/'.join((S3_FILES_FOLDER, filename))
            k.set_contents_from_filename(f)
            send_files.append(k.key)
    
    # Remove rs in filename
    full_filenames = ['/'.join((S3_FILES_FOLDER, filename)) for filename in files]
    for s3_filename, s3_filedate in rs.items():
        if s3_filename not in full_filenames:
            bucket.delete_key(s3_filename)

    # blobs
    now_date = DateTime().strftime('%Y%m%d%H%M')
    k.key = '/'.join((S3_BLOBS_FOLDER, now_date, S3_BLOBS_FILENAME))
    k.set_contents_from_filename(blob_bk_filename)
    send_files.append(k.key)

def _comp_func(l):
    return DateTime(l[1])

def remove_s3_blobs(aws_id, aws_key, bucket_name, blob_store_len):
    conn = S3Connection(aws_id, aws_key)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    list_folders = list(bucket.list(S3_BLOBS_FOLDER))
    diff_len = len(list_folders) - blob_store_len
    if diff_len > 0:
        sorted_folders = sorted([(key.name, key.last_modified) for key in list_folders],
                    key=_comp_func)
        for name, date in sorted_folders[:diff_len]:
            bucket.delete_key(name)
            

def backup_main(bin_dir, blobstorage_path, backup_location, blob_bk_location, 
                use_s3, aws_id, aws_key, bucket_name, blob_store_len):
    """Main method, gets called by generated bin/bkups3."""
    backup = os.path.join(bin_dir, 'backup')
    os.system(quote_command([backup]))
    
    # blobs
    blob_archive = "blobs.tar.gz"
    blob_bk_filename = make_tar(blobstorage_path, 
                        os.path.join(blob_bk_location, blob_archive))
    logger.info("Backing up blobstorage files: %s .",
                blob_bk_filename)

    # To S3
    if use_s3:
        stror_files = send_s3(aws_id, aws_key, bucket_name, backup_location, blob_bk_filename)
        logger.info("Sending S3 : %s .",
                    stror_files)
        # Remuve over blob_store_len
        remove_files = remove_s3_blobs(aws_id, aws_key, bucket_name, blob_store_len)
        logger.info("Remove S3 : %s .",
                    remove_files)

if __name__ == '__main__':
    backup_main()

