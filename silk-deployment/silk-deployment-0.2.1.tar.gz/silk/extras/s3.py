import os
import boto
from boto.s3.key import Key

def push_s3(azn_key, azn_secret, s3bucket, localdir, s3dir):
    """Recurses through localdir, uploading each file it finds into the corresponding
    path in s3dir"""
    conn = boto.connect_s3(azn_key, azn_secret)
    bucket = conn.get_bucket(s3bucket)
    tree = os.walk(localdir)
    for folder in tree:
        folderpath = folder[0]
        subfiles = folder[2]
        for file in subfiles:
            localfile = os.path.join(folderpath, file)
            trimmed_dir = folderpath[len(localdir):]
            #os.path.normpath cleans out any double slashes //
            #warning: if run from windows the slashes will get turned into backslashes
            s3file = os.path.normpath("/".join((s3dir, trimmed_dir, file)))
            print "pushing %s to %s" % (localfile, s3file)
            k = Key(bucket)
            k.key = s3file
            k.set_contents_from_filename(localfile)
            k.set_acl('public-read')
