import sys
import shutil
from stellaris.index.virtuoso import VirtuosoCommandClient

if __name__ == '__main__':
    spool_dir = '/tmp/%s/virtuoso/spool/add.rdf' % sys.argv[1]
    shutil.copyfile('/home/mikael/lab/stellaris/tests/data/add.rdf', spool_dir)
    c = VirtuosoCommandClient('/home/mikael/_install/bin/isql', 1112)
    c.replace(spool_dir, 'http://blub')

# REPLACE_GRAPH('/tmp/tmptJa7L5/virtuoso/spool/add.rdf','http://blub');
# REPLACE_GRAPH('/tmp/tmptJa7L5/virtuoso/spool/replace.rdf','http://blub');

print "REPLACE_GRAPH('/tmp/%s/virtuoso/spool/add.rdf','http://blub');" % sys.argv[1]
