from stellaris.index.virtuoso import VirtuosoIndex, VirtuosoInstance
from tempfile import mkdtemp
from stellaris.graph import FileGraph
import time

if __name__ == '__main__':
    bind = '127.0.0.1:9080'

#        dav_url = 'http://localhost:8891/DAV/home/dav/rdf_sink/'
    sparql_url = 'http://localhost:8891/sparql/'
    tmp_dir = mkdtemp()

    index = VirtuosoIndex('/home/mikael/_install/', './tests/data/virtuoso.ini', sparql_url, tmp_dir, isql_port=1112, baseuri='http://%s/' % bind)
    print "started virtuoso in: ", tmp_dir

    time.sleep(5)

    g_name = 'http://blub'
    g = FileGraph(g_name, './tests/data/add.rdf')

    index.replace(g_name, g)
