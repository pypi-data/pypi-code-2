import os
import sys
import pymongo
import gridfs

conn = pymongo.Connection()
db = conn.test
fs = gridfs.GridFS(db, 'files')

for fname in os.listdir(sys.argv[1]):

    fullname = os.path.join(sys.argv[1], fname)
    print fname
    fp = fs.new_file(_id=fname)
    fp.write(file(fullname).read())
    fp.close()




