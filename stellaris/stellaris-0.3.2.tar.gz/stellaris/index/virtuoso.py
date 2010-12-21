# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, urllib, time, sys, re, socket, signal, pexpect

from urllib import urlencode
from urlparse import urljoin, urlparse
from hashlib import md5
from tempfile import mkdtemp, mkstemp
from subprocess import Popen, PIPE
from shutil import rmtree

from datetime import datetime, timedelta
from benri.client.client import Client, NotFound

from stellaris.index import Index
from stellaris.index.exceptions import IndexReplaceFailed, IndexDeleteFailed, IndexQueryFailed, IndexNotAvailable

class VirtuosoInstance(object):
    def __init__(self, virtuoso_prefix, virtuoso_cfg, config_commands, isql_port=1112):
        """
        ``virtuoso_prefix`` - path to the virtuoso installation
        ``virtuoso_cfg`` - Path to the configuration-file for virtuoso
        ``config_commands`` - A list of commands executed via isql used to 
                              configure the virtuoso instance.
        """

        self.__virtuoso_prefix = virtuoso_prefix
        virtuoso_exec = os.path.join(virtuoso_prefix, 'bin/virtuoso-t')
        self.proc = Popen([virtuoso_exec, "-f", "-c", virtuoso_cfg], stdout=PIPE, stderr=PIPE)

        started = False

        isql_exec = os.path.join(virtuoso_prefix, 'bin/isql')

        total_sleep = 0.0

        while not started and total_sleep < 30.0:
            isql = pexpect.spawn("%s %d" % (isql_exec, isql_port))
            i = isql.expect(['Connected to OpenLink Virtuoso', 'SQL> ', pexpect.EOF])

            if i == 0:
                started = True

            time.sleep(1.0)
            total_sleep += 1.0


        if not started:
            raise IndexNotAvailable('Failed to start the virtuoso backend, check your configuration')

        self._configure(isql_exec, config_commands)

    def _configure(self, isql_exec, commands):
        isql = pexpect.spawn("%s 1112" % isql_exec)
        isql.expect('SQL> ')

        for command in commands:
            isql.sendline(command)
            isql.expect('SQL> ')

#        print isql.before
        isql.sendline('EXIT;')
 
    def clean(self):
        rmtree(self.__tmp_dir)
        
    def stop(self):
        os.kill(self.proc.pid, signal.SIGTERM)
        self.proc.wait()

class VirtuosoCommandClient(object):
    def __init__(self, isql_exec, port):
        self.__isql_exec = isql_exec
        self.__port = port
        self.__proc = None

    def execute(self, cmd):
        if self.__proc == None or self.__proc.isalive() == False:
            self.__proc = pexpect.spawn("%s %i" % (self.__isql_exec, self.__port))
            self.__proc.expect('SQL> ')

        self.__proc.sendline(cmd)
        self.__proc.expect('SQL> ')

#        print self.__proc.before

    def replace(self, path, graph_name):
#        execute("DB.DBA.RDF_LOAD_RDFXML_MT(file_to_string_output('%s'), '', '%s');" % (path, graph_name))
        self.execute("REPLACE_GRAPH('%s', '%s');" % (path, graph_name))

    def delete(self, graph_name):
#        execute("DB.DBA.RDF_LOAD_RDFXML_MT(file_to_string_output('%s'), '', '%s');" % (path, graph_name))
        self.execute("DELETE_GRAPH('%s');" % (graph_name))

    def close(self):
        # exit the commandline client
        if self.__proc != None and self.__proc.isalive():
            self.__proc.sendline('EXIT;')

class VirtuosoClient(object):

    def __init__(self, sparql_url, log=None):
        self.__sparql = Client(sparql_url)
        
        try:
            self.__sparql.get('')
        except NotFound, e:
            raise IndexNotAvailable("Could not use Virtuoso's SPARQL endpoint at URL: %s" % sparql_url)
        except socket.error, e:
            raise IndexNotAvailable('Virtuoso sparql-endpoint not found: %s' % sparql_url)

        self.log = log
        
    def query(self, query, format='xml'):
        headers = {}
        # support for construct-queries
        if format == 'rdf':
            headers['Accept'] = 'application/rdf+xml'
        else:
            headers['Accept'] = 'application/sparql-results+%s' % format

        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        data = urlencode({'query': query, 'format': format})
        stat, resp = self.__sparql.post('/?default_graph_uri=&named_graph_uri=', data, headers=headers)

        if stat['status'] != '200':
            raise IndexQueryFailed(resp)

        return resp
        
class VirtuosoIndex(Index):

    def __init__(self, install_prefix, config_tmpl, sparql_url, db_prefix, baseuri="http://stellaris.gac-grid.org/", isql_port=1112, log=None):
        """
        Uses a Virtuoso database for indexing graphs.
        ``install_prefix`` - path to the virtuoso installation
        ``config_tmpl`` - Path to a configuration-file template for virtuoso        
        ``sparql_url`` - URL to virtuoso's SPARQL endpoint
        ``db_prefix`` - prefix-path to the stellaris data environment
        ``baseuri`` - prefix-name for graphs, usually based on the server FQDN
        """

        Index.__init__(self, baseuri)
        
        self.log = log
        self.__baseuri = baseuri
        self.__config_tmpl = config_tmpl
        self.__install_prefix = install_prefix
        self.__db_prefix = db_prefix

        self._load_instance(reset=False, isql_port=isql_port)
        self.__client = VirtuosoClient(sparql_url, log=log)
        isql_exec = os.path.join(install_prefix, 'bin/isql')
        self.__cmd_client = VirtuosoCommandClient(isql_exec, isql_port)

    def init_store(self):
        if self.log:
            self.log.debug("Initialization of the virtuoso index complete.")

    def _load_instance(self, reset=False, isql_port=1112):
        """
        ``reset`` - if this is true, the instance environment is reset and all
                    indexed data is removed.
        """
        self.__instance_dir = os.path.join(self.__db_prefix, 'virtuoso')
        self.__virtuoso_db_dir = os.path.join(self.__instance_dir, 'db')
        self.__spool_dir = os.path.join(self.__instance_dir, 'spool') 

        virtuoso_ini = os.path.join(self.__instance_dir, 'virtuoso.ini')

        if reset:
            rmtree(self.__instance_dir)

        if not os.path.exists(self.__instance_dir):
            os.mkdir(self.__instance_dir)
            os.mkdir(self.__virtuoso_db_dir)
            os.mkdir(self.__spool_dir)
            virtuoso_ini = self._replace_cfg()

        # first remove all data and then load the file into the graph
        create_procedure = """
create procedure REPLACE_GRAPH (in path varchar, in graph_uri varchar) {
  DELETE FROM RDF_QUAD WHERE G = DB.DBA.RDF_MAKE_IID_OF_QNAME (graph_uri);
  DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output(path), graph_uri, graph_uri);
}
"""

        delete_procedure = """
create procedure DELETE_GRAPH (in graph_uri varchar) {
  DELETE FROM RDF_QUAD WHERE G = DB.DBA.RDF_MAKE_IID_OF_QNAME (graph_uri);
}
"""

        # grant update to the sparql user and initialize the indices
        commands = ["USER_GRANT_ROLE('SPARQL','SPARQL_UPDATE',0);",
                    "CREATE BITMAP index RDF_QUAD_POGS on DB.DBA.RDF_QUAD (P,O,G,S);",
                    "CREATE BITMAP index RDF_QUAD_POSG on DB.DBA.RDF_QUAD (P,O,S,G);",
                    "CREATE BITMAP index RDF_QUAD_SPOG on DB.DBA.RDF_QUAD (S,P,O,G);",
                    "CREATE BITMAP index RDF_QUAD_SOPG on DB.DBA.RDF_QUAD (S,O,P,G);",
                    "CREATE BITMAP index RDF_QUAD_OPSG on DB.DBA.RDF_QUAD (O,P,S,G);",
                    "CREATE BITMAP index RDF_QUAD_OSPG on DB.DBA.RDF_QUAD (O,S,P,G);",
                    create_procedure,
                    delete_procedure]

        if self.log:
            self.log.info('Starting a virtuoso instance with env %s.' % self.__instance_dir)

        self.__instance = VirtuosoInstance(self.__install_prefix, virtuoso_ini, commands, isql_port=isql_port)

    def _replace_cfg(self):
        prefix = self.__install_prefix
        if prefix.endswith('/'):
            prefix = prefix[:-1]

        f = file(self.__config_tmpl, 'r')
        cfg = []

        replace_words = [('$VIRTUOSO_PREFIX', self.__install_prefix), 
                         ('$DB_PREFIX', self.__virtuoso_db_dir),
                         ('$SPOOL_DIR', self.__spool_dir)]
        for l in f:
            for (word, value) in replace_words:
                if word in l:
                    l = l.replace(word, value)

            cfg.append(l)

        f.close()

        # setup the config-dir for the virtuoso-file, this can be edited
        # later if necessary
        cfg_path = os.path.join(self.__instance_dir, 'virtuoso.ini')
        f_out = file(cfg_path, 'w')
        f_out.write('\n'.join(cfg))
        f_out.close()

        return cfg_path

    def _rewrite_query(self, query):
        """
        Re-writes the query by replacing any FROM NAMED to the internal
        name used in virtuoso
        
        Ex:
        FROM NAMED </a/test>
        =>
        FROM NAMED </DAV/home/dav/rdf_sink/1234>
        """
        
        # TODO: Filter out collections which the user is not authorized for
        def replace_from_named(re_match):
            uri = re_match.group('uri')
#            print uri, self.__baseuri
            # check if this is a local uri, assume that if the uri is prefixed
            # by the baseuri it is a local uri
            if uri.startswith(self.__baseuri):
                try:
                    context = self.contexts[uri]
                except KeyError, e:
                    return ''

                # assume that internal graph names start with '/'
                return 'FROM NAMED <%s%s>\n' % (self.__virtuoso_prefix, context)
            
            # use from, since this is likely to work better with most
            # index backends
            return 'FROM NAMED <%s>\n' % uri
                
        # find all rows with from named
        p = re.compile(r'(from named <(?P<uri>.*)>)', re.IGNORECASE)
        new_q = p.sub(replace_from_named, query)
        return new_q
                   
    def close(self):
        self.__instance.stop()
#        self.gc.stop()

    def delete(self, graph_uri):
        """
        Deletes the graph with the given ``graph_uri`` from the index.
        
        ``graph_uri`` - uri of the graph to delete.
        """
            
#        if not graph_uri in self.contexts:
            # graph is not stored, just return
#            return

        # remove from the store and then remove from the local contexts
#        self.__client.delete_context(context=self.contexts[graph_uri])

        # remove from the virtual DAV graph using SPARUL
        self.__cmd_client.delete(graph_uri)

#        delete_query = """drop graph <%s>""" % (graph_uri)
#        self.__client.query(delete_query)

#        delete_virtual = """DELETE FROM <%s> { WHERE GRAPH <%s%s> { ?s ?p ?o }}""" % (self.__virtuoso_prefix, self.__virtuoso_prefix, self.contexts[graph_uri])

#        del self.contexts[graph_uri]
            
    def replace(self, graph_uri, graph):
        """
        Overwrites the graph stored at ``graph_uri`` with the given ``graph``.
        
        ``graph_uri`` - overwrite graph with this name
        ``graph`` - use this graph to overwrite the indexed graph
        """
        (fd, tmp_file) = mkstemp(dir=self.__spool_dir)
        bytes_written = os.write(fd, graph.serialized)
        os.close(fd)

        graph_len = len(graph.serialized)

        if bytes_written != graph_len:
            os.remove(tmp_file)
            raise IndexReplaceFailed('Wrote %d/%d bytes of graph %s to file %s' % (bytes_written, graph_len, graph_uri, tmp_file))

        # virtuoso inserts the file into a graph as well for some 
        # unknown reason, so we are forced to drop that extra graph...
        
        # drop silent graph <%s> 
        #  drop silent graph <file://%s>
#        print "\nloading file: " + tmp_file + " into " + graph_uri
#        replace_query = """load <file://%s> into graph <%s>""" % (tmp_file, graph_uri)

#        try:
#            self.__client.query(replace_query)
#        except Exception, e:
#            os.remove(tmp_file)
#            raise IndexReplaceFailed(e)

        self.__cmd_client.replace(tmp_file, graph_uri)
        os.remove(tmp_file)

    def query(self, query, format="xml", out_file=False):
        """
        Exectues the given query over the index.
        """
#        new_q = self._rewrite_query(query)
        res = self.__client.query(query, format=format)

        if out_file:
            (fd, tmp_file) = mkstemp(dir=self.__spool_dir)
            bytes_written = os.write(fd, res)
            #print "results to file: ", bytes_written, len(res)
            os.close(fd)
            return tmp_file
        else:
            return res
         
    def __delitem__(self, graph_uri):
        """Alias for delete."""
        self.store.delete(graph_uri)
                
    def __setitem__(self, graph_uri, graph):
        """Alias for replace."""
        self.replace(graph_uri, graph)
        
    def __contains__(self, graph_uri):
        return graph_uri in self.contexts

if __name__ == '__main__':
#    import hotshot, psyco

    from stellaris.graph import FileGraph
    dav_url = 'http://localhost:8890/DAV/home/dav/rdf_sink/'
    sparql_url = 'http://localhost:8890/sparql/'    
    store = VirtuosoIndex(dav_url, sparql_url, 'dav', 'dav', baseuri='http://test.org/')

    graph_name = 'http://test.org/hello'
    g1 = FileGraph(graph_name, './tests/data/add.rdf')
    store.replace(graph_name, g1)

    graph_name = 'http://test.org/hello2'
    g2 = FileGraph(graph_name, './tests/data/update.rdf')
#    store.replace(graph_name, g2)

    graph_name = 'http://test.org/hello3'
    g3 = FileGraph(graph_name, './tests/data/replace.rdf')
#    store.replace(graph_name, g3)

    query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang ?g
 #                  FROM NAMED <http://local.virt/DAV/home/dav/rdf_sink/81dd9250bf5a53338f888fa79719fb57>
                   #FROM <http://stellaris.zib.de:24000/context/test>
                   FROM NAMED <http://test.org/hello>
                   #FROM NAMED <http://test.org/hello2>                   
                   WHERE { graph ?g { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }}
                """

#    query = """
#    select ?g ?s ?p ?o
#    from named <http://local.virt/DAV/home/dav/rdf_sink/81dd9250bf5a53338f888fa79719fb57>
#    from named <http://test.org/hello2>
#    from named <http://test.org/hello3>    
#    from named <http://test.org/hello>    
#    where { graph <http://localhost:8890/DAV/home/dav/rdf_sink/> { ?s ?p ?o }}
#    where { graph ?g { ?s ?p ?o }}
#    """
    
#    query = """
#select distinct ?s ?p ?o where { graph <http://local.virt/DAV/home/dav/#rdf_sink/81dd9250bf5a53338f888fa79719fb57> { ?s ?p ?o } }
#    """

    print store.contexts
    print store.query(query, format='json')
    
#    store.replace(graph_name, g1)
    store.delete(g1.uri)
    
    try:
        print store.contexts[g1.uri]
    except KeyError, e:
        pass

#    store.delete(g2.uri)
#    store.delete(g3.uri)
    print store.query(query, format='json')
        
    store.close()
    
#    psyco.full()
#    prof = hotshot.Profile("hotshot_query_stats_psyco")
#    prof.runcall(main)
#    prof.close()
#    main()
