# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import optparse, os, sys, mimetypes, csv, tarfile, math

from ConfigParser import SafeConfigParser
from urlparse import urljoin
from tempfile import mkstemp

from stellaris.client import GraphClient, QueryClient, SystemClient
from stellaris.client.parsers import SPARQLResults
from stellaris.client import __VERSION__

from benri.client.client import Conflict, Unauthorized

class ConfigFileMissing(Exception): pass

class ClientConfig(object):
    def __init__(self, path):
        self.__path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)
        
        self.__cfg_file = os.path.join(self.__path, 'client.cfg')
        self._parse()

    @property
    def base_path(self):
        return self.__path
        
    @property
    def service_url(self):
        return self.__config['service']['service_url']
    
    @property
    def prefix(self):
        return self.__config['service']['prefix']

    @property
    def graph_url(self):
       return urljoin(self.service_url, self.prefix)

    @property
    def default_index(self):
        return self.__config['service']['default_index']
    
    @property
    def query_prefix(self):
        return os.path.join(self.prefix, 'query/')

    @property
    def system_prefix(self):
        return os.path.join(self.prefix, 'system/')

    @property
    def key_path(self):
        return os.path.abspath(os.path.expanduser(self.__config['security']['private_key']))

    @property
    def cert_path(self):
        return os.path.abspath(os.path.expanduser(self.__config['security']['certificate']))
    
    def exists(self):
        return os.path.exists(self.__cfg_file)

    def _parse(self):
        config = SafeConfigParser()
        config.read([self.__cfg_file])
        
        data = {}
        
        for sec in config.sections():
            data[sec] = {}
            
            for (item,value) in config.items(sec):
                data[sec][item] = value

        self.__config = data
        
    def _write(self, data=None):
        """
        Writes the current config to disk or takes the given config and writes
        it to disk.
        """
        cfg = SafeConfigParser()
        
        if not data:
            data = self.__config
            
        for section in data:
            cfg.add_section(section)
            for item in data[section]:
                cfg.set(section, item, data[section][item])

        cfg.write(file(self.__cfg_file, 'w'))
        self.__config = data            

    def config_guide(self):
        if not self.exists():
            default_values = {'service_url': 'http://localhost:24000/',
                              'private_key': '',
                              'certificate': '',
                              'prefix': '/',
                              'default_index': 'query'}
        else:
            default_values = {'service_url': self.service_url,
                              'prefix': self.prefix,
                              'private_key': self.key_path,
                              'certificate': self.cert_path,
                              'default_index': self.default_index}

        def read_data(msg, default):
            return raw_input('%s [%s]> ' % (msg, str(default))).strip() or default
            
        ret = {'service': {}, 'security': {}}
        print "StellarIS client configuration guide."
        print "-------------------------------------"
        print
        print "This guide will create a new client configuration file."
        print "If you want to change the values, then edit the file directly or"
        print "re-run this guide by giving the option --configure."
        print 
        print "Please enter the default Stellaris service you want to use."
        ret['service']['service_url'] = read_data('Service URL', default_values['service_url'])
        print
        print "A stellaris service may be running at a certain path relative to the Service URL."
        print "If this is the case for the used service, please the service prefix below."
        ret['service']['prefix'] = read_data('Service prefix', default_values['prefix'])
        print
        print "A service can expose different indices to exectue queries over."
        print "Please enter the name of the default index you want to use. This"
        print "value is overridden by using the --index option when calling the client."
        ret['service']['default_index'] = read_data('Default index', default_values['default_index'])
        print
        print "X.509 certificates are used to authenticate a connecting client"
        print "In order to enable client authentication please enter the path to"
        print "your public (certificate) and private key."
        ret['security']['private_key'] = read_data('Private Key', default_values['private_key'])

        if not os.path.exists(ret['security']['private_key']):
            ret['security']['private_key'] = ''

        ret['security']['certificate'] = read_data('Certificate', default_values['private_key'])

        if not os.path.exists(ret['security']['certificate']):
            ret['security']['certificate'] = ''

        print "Saving configuration file: %s." % self.__cfg_file
        print
        try:
            self._write(data=ret)
        except Exception, e:
            sys.exit("Could not write the configuration file: %s\n" % str(e))
        print "Configuration file was written successfully written. Run the client"
        print "again with --help to get information about available commands."
        print

class ConsoleClient(object):
    
    def __init__(self, config_path):
        config_path = os.path.abspath(os.path.expanduser(config_path))
        
        cfg = ClientConfig(config_path)
        
        if not cfg.exists():
            cfg.config_guide()
            
        # make sure that .rdf is translated to the correct mime-type
        mimetypes.add_type('application/rdf+xml', '.rdf')
        self.cfg = cfg

        self.graph_client = GraphClient(self.cfg.service_url, base_path=self.cfg.base_path, prefix=self.cfg.prefix, key=self.cfg.key_path, cert=self.cfg.cert_path)
        self.system_client = SystemClient(self.cfg.service_url, base_path=self.cfg.base_path, prefix=self.cfg.prefix, key=self.cfg.key_path, cert=self.cfg.cert_path)
        
    def _init_optparser(self):
        p = optparse.OptionParser(version="Stellaris Client %s" % __VERSION__, usage="%prog [options] <command>")
        p.add_option("-s", "--service", action="store", type="string", dest="service",
                     default="http://localhost:24000", help="The service URL that the client will connect to.")
        p.add_option("", "--configure", action="store_true", dest="configure",
                     default=False, help="Run the configuration guide.")
        p.add_option("-i", "--index", action="store", dest="index",
                     default='query', help="Indicates what index to use for processing a query.")
        p.add_option("", "--key", action="store", dest="key_path",
                     default=None, help="Absolute path to a private key used for SSL/TLS.")
        p.add_option("", "--cert", action="store", dest="cert_path",
                     default=None, help="Absolute path to a certificate used for SSL/TLS.")
        p.add_option("", "--recursive", action="store_true", dest="recursive",
                     default=False, help="Performs the operation recursively.")
        p.add_option("-o", "--output", action="store", dest="output_path",
                     default=None, help="Filename where output data is written, defaults to stdout.")
        p.add_option("-f", "--format", action="store", dest="format",
                     default='xml', help="Defines the output format.")
        p.add_option("", "--verbose", action="store_false", dest="verbose",
                     default=True, help="Reports more than failures (default).")
                     
        p.add_option("", "--graph-version", action="store", dest="version",
                     default=None, help="Version of the retrieved graph.")

        return p

    def _collection_backup(self, collection_name, output_path, recursive=False):
        """
        Retrieves all the graphs in the collection and stores them in a tar-file
        defined by ``output_path``. If recursive is ``True``, all 
        sub-collections are searched recursively for graphs which are also
        added to the backup.
        
        ``collection_name`` - name of the collection to backup
        ``output_path`` - file-name of the compressed file containing the backup
        ``recursive`` - Indicates if the backup should search in sub-collections
        """        
        cols, graphs = self.system_client.collection_retrieve(collection_name, recursive=recursive)

        if len(graphs) <= 0:
            print "No graphs found at %s." % collection_name
            return 

        def dump_to_file(data):
            (fd, tmp_name) = mkstemp()

            f = os.fdopen(fd, 'w+')
            f.write(data)
            
            f.close()
            
            return tmp_name

        tar = tarfile.open(output_path, 'w:gz')

        num_graphs = len(graphs)
        print "Starting backup of %d graphs." % num_graphs
        
        backed_up = 0
        ticks = 0
        max_ticks = 20
        ticks_step = float(max_ticks)/num_graphs

        (fd, backup_index_name) = mkstemp()
        backup_index = os.fdopen(fd, 'w+')

        for g in graphs:
            try:
                stat, graph_data = self.graph_client.retrieve(g)
                file_name = dump_to_file(graph_data)
                file_info = tar.gettarinfo(file_name)
                # discard leading slash
                backup_index.write("%s\t%s\n" %(g, stat['etag']))
                file_info.name = str(g[1:])
                tar.addfile(file_info, file(file_name))
                os.remove(file_name)

            except Exception, e:
                # print out that the data could not be retrieved, --verbose
#                print e
                raise
            backed_up += 1
            
            #print backed_up, num_graphs, float(backed_up)/num_graphs, float(backed_up)/num_graphs > ticks/max_ticks
            if float(backed_up)/num_graphs > float(ticks)/max_ticks:
                ticks += int(math.ceil(ticks_step))
                
                if ticks > max_ticks:
                    ticks = max_ticks

            sys.stdout.write("Progress: [%s%s], current: %s\r" % ("="*ticks, " "*(max_ticks-ticks), g))
            sys.stdout.flush()
            
        backup_index.close()
        file_info = tar.gettarinfo(backup_index_name)
        file_info.name = '.backup_index.txt'
        tar.addfile(file_info, file(backup_index_name))
        os.remove(backup_index_name)
        tar.close()
        print

    def _restore_backup(self, file_path, prefix='/', replace=False):
        """
        Restore all graphs from a backed-up file. If the graph already exists 
        at the server it is ignored since this backup is assumed to be older
        than any files at the server. Otherwise, if the graph does not exist, 
        it is created. To replace existing files, set ``replace`` to True. 

        ``file_path`` - path to a tar-file created with `_collection_backup`
        ``prefix`` - used as prefix when uploading the file to the service
        ``replace`` - indicates if existing files should be overwritten
        """
        tar = tarfile.open(file_path, 'r:gz')
        
        try:
            backup_index_info = tar.getmember('.backup_index.txt')
        except KeyError, e:
            print "The tar-archive (%s) is not a valid stellaris backup-file." % file_path
            return

        backup_index = tar.extractfile(backup_index_info)

        files = dict([tuple(l.split("\t")) for l in backup_index])

        mime_type = 'application/rdf+xml'

        num_graphs = len(files)
        print "Starting restore of %d graphs." % num_graphs
        
        backed_up = 0
        ticks = 0
        max_ticks = 20
        ticks_step = float(max_ticks)/num_graphs

        for graph in tar:
            graph_name = '/' + graph.name
            try:
                version = int(files[graph_name].strip())
            except KeyError, e:
                # file was not in the index-file, so ignore it
                continue
            
            if not graph_name.startswith(prefix):
                graph_name = prefix + graph_name[1:]

            try:
                self.graph_client.create(graph_name, tar.extractfile(graph), mime_type)
            except Conflict, e:
                if replace:
                    self.graph_client.replace(graph_name, tar.extractfile(graph), mime_type)
            except Exception, e:
                print "Could not restore %s, error: %s" % (graph_name, str(e))

            backed_up += 1

            #print backed_up, num_graphs, float(backed_up)/num_graphs, float(backed_up)/num_graphs > ticks/max_ticks
            if float(backed_up)/num_graphs > float(ticks)/max_ticks:
                ticks += int(math.ceil(ticks_step))

                if ticks > max_ticks:
                    ticks = max_ticks

            sys.stdout.write("Progress: [%s%s], current: %s\r" % ("="*ticks, " "*(max_ticks-ticks), graph_name))
            sys.stdout.flush()

    def _bulk_upload(self, prefix, dir_path):
        """
        
        """
        dir_path = os.path.abspath(os.path.expanduser(dir_path))

        def gen_paths(root_path):
            for dirpath, dirnames, filenames in os.walk(root_path):
                for f in filenames:
                    yield os.path.join(dirpath, f)

        for path in gen_paths(dir_path):
            graph_name = os.path.join(prefix, path.replace(dir_path, '')[1:])
            mime_type, _ = mimetypes.guess_type(path)
            
            if mime_type == 'text/rdf':
                mime_type = 'application/rdf+xml'

            data = self._read_data(path)
            try:
                self.graph_client.create(graph_name, data, mime_type)
            except Conflict, e:
                self.graph_client.update(graph_name, data, mime_type) 
            except Exception, e:
                print "Failed to upload graph: ", path, e
        
    def _error_msg(self, msg):
        sys.exit("[ERROR]: %s" % msg)
                    
    def execute_command(self, args):
        op = self._init_optparser()
        (opts, args) = op.parse_args(args=args)
        
        cfg = self.cfg
        
        if opts.configure:
            cfg.config_guide()
            sys.exit(1)
        
        if len(args) < 1:
            op.print_version()
            op.print_help()
            sys.exit(1)        
                   
        module = args[0]
        
        self.dispatch(module, opts, args[1:])

    def dispatch(self, module, opts, args):
        try:
            f = getattr(self, '_dispatch_%s' % module)
        except AttributeError, e:
            self._error_msg('%s is not a valid command' % module)
            
        f(opts, args)
        
    def _dump_data(self, data, path=None):
        if not path:
            f = sys.stdout
        else:
            if os.path.exists(path):
                i = 1
                path += '.%s' % str(i)
                
                while os.path.exists(path):
                    i += 1
                    path = path[:path.rfind('.')+1] + str(i)
                
            f = file(path, 'w')

        f.write(data)
        f.close()      

    def _read_data(self, path):
        if not os.path.exists(path):
            self._error_msg('Input file does not exist: %s' % path)
        return ''.join([l for l in file(path)])

    def _opt_arg(self, args, index, default=None):
        try:
            return args[index]
        except IndexError, e:
            return default

    def _opt_arg_fail(self, args, index, msg=''):
        val = self._opt_arg(args, index) 
        if val == None:
            self._error_msg(msg)
        return val
                                                
    # query <file_path> [output_path] [format]
    # query indices

    def _dispatch_query(self, opts, args):
        index = opts.index
        if index == None:
            index = self.cfg.default_index
            
        client = QueryClient(self.cfg.service_url, index_name=index, base_path=self.cfg.base_path, prefix=self.cfg.prefix, key=self.cfg.key_path, cert=self.cfg.cert_path)

        index_or_path = self._opt_arg_fail(args, 0, msg='"indices" nor query input file defined.')
        
        in_path = index_or_path
        output_path = opts.output_path # self._opt_arg(args, 1)
        format = opts.format # self._opt_arg(args, 2, 'xml')        
        
        try:
            data = client.query(self._read_data(args[0]), format=format)
            self._dump_data(data, path=output_path)
        except Exception, e:
            sys.exit("Could not finish query - %s" % str(e))

    # graph create <name> <file_path>
    # graph retrieve <name> [output_path] [version]
    # graph delete <name>
    # graph update <name> <file_path>
    # graph remove <name> <file_path>
    # graph replace <name> <file_path>
    # graph append <name> <file_path>
    # graph atomic_operations <name> <file_path>
    # graph bulk <prefix> <directory>
    
    def _dispatch_graph(self, opts, args):
        op = self._opt_arg_fail(args, 0, 'Graph command not defined.')
        
        client = self.graph_client 

        graph_name = self._opt_arg_fail(args, 1, 'Graph name not defined.')
        if op == 'retrieve':
            output_path = opts.output_path
            version = opts.version
            try:
                stat, data = client.retrieve(graph_name, version=version)
            except Exception, e:
                sys.exit("Error retrieving graph %s - %s" %(graph_name, str(e)))

            self._dump_data(data, path=output_path)
        elif op == 'delete':
            try:
                client.delete(graph_name)
            except Exception, e:
                sys.exit("Error deleting graph %s - %s" %(graph_name, str(e)))

        elif op == 'create':
            input_path = self._opt_arg_fail(args, 2, 'Cannot create graph without an input file.')
            mime_type, _ = mimetypes.guess_type(input_path)
            try:
                client.create(graph_name, self._read_data(input_path), mime_type)
            except Conflict, e:
                sys.exit("%s already exist, try `graph replace` instead." % graph_name)
            except Exception, e:
                sys.exit("Error creating graph %s - %s\n" %(graph_name, str(e)))
                
                
        elif op in ['update', 'remove', 'replace', 'append']:
            f = getattr(client, 'graph_%s' % op)
            # name + file_path
            input_path = self._opt_arg_fail(args, 2, 'Cannot modify a graph without an input file.')
            mime_type, _ = mimetypes.guess_type(input_path)            
            try:
                f(graph_name, self._read_data(input_path), mime_type)
            except Exception, e:
                sys.exit("Error when executing %s on %s - %s" %(op, graph_name, str(e)))

        elif op =='bulk':
            dir_path = self._opt_arg_fail(args, 2, 'Bulk directory not defined..')
            self._bulk_upload(graph_name, dir_path)
        elif op == 'atomic_operations':
            input_path = self._opt_arg_fail(args, 2, 'Cannot apply atomic operations without an input file.')
            ops = []
            try:
                reader = csv.reader(open(input_path, "rb"))
                for row in reader:
                    if row[0] in ['append', 'remove', 'update']:
                        ops.append((row[0], os.path.abspath(row[1].strip())))
                    else:
                        sys.exit('%s contains an invalid operation: %s' % (input_path, row[0]))
            except IOError, e:
                if e.errno == 2:
                    sys.exit('Could not find atomic operations input file: %s' % input_path)

            try:
                client.graph_atomic_operations(graph_name, ops)
            except Exception, e:
                sys.exit("Error performing atomic operations on %s - %s" %(graph_name, str(e)))

        else:
            self._error_msg('%s is not a valid graph command.' % op)
            
    # collection add_group <collection_name> <group_name> <rights>
    # collection remove_group <collection_name> <group_name>
    # collection list <collection_name>
    # collection backup <collection_name> <output_path> [<recursive>]
    # collection restore <collection_prefix> <backup_file> [<overwrite>]
    
    def _dispatch_collection(self, opts, args):
        client = self.system_client

        op = self._opt_arg_fail(args, 0, 'Collection command not defined.')

        collection_name = self._opt_arg_fail(args, 1, 'Collection name not defined.')
        
        if op == 'list':
            try:
                collections, graphs = client.collection_retrieve(collection_name, recursive=opts.recursive)
            except Exception, e:
                sys.exit("Could not list collections - %s" % str(e))

            print 'Sub-collections:'
            for collection in collections:
                print collection
                
            print
            print 'Graphs:'
            for graph in graphs:
                print graph
        elif op == 'add_group':
            group_name = self._opt_arg_fail(args, 2, 'Group name necessary when adding a new group.')
            rights = self._opt_arg_fail(args, 3, 'The rights for the new group is missing.')

            try:
                client.collection_add_group(collection_name, group_name, access_rights=rights)
            except Exception, e:
                sys.exit("Could not add group %s to the collection %s - %s" % (group_name, collection_name, str(e)))

        elif op == 'remove_group':
            group_name = self._opt_arg_fail(args, 2, 'Cannot remove group from collection without a group name.')

            try:
                client.collection_remove_group(collection_name, group_name)
            except Exception, e:
                sys.exit("Could not remove group %s from collection %s - %s" % (group_name, collection_name, str(e)))

        elif op == 'backup':
            output_path = self._opt_arg_fail(args, 2, 'Output file name is missing.')
            recursive = opts.recursive
            self._collection_backup(collection_name, output_path, recursive=recursive)
        elif op == 'restore':
            input_path = self._opt_arg_fail(args, 2, 'Input file path is missing.')
            self._restore_backup(input_path, prefix=collection_name)
#        elif op == 'retrieve':
#            output_path = self._opt_arg_fail(args, 2, 'Output file name is missing.')
#            recursive = opts.recursive
        elif op == 'delete':
            try:
                client.collection_delete(collection_name, recursive=opts.recursive)
            except Exception, e:
                sys.exit("Could not delete collection %s - %s" % (collection_name, str(e)))
        else:
            self._error_msg('%s is not a valid collection command.' % op)
            
    # group list
    # group create <name>
    # group delete <name>
    # group retrieve <name>
    # group add <group_name> <user_name>
    # group remove <group_name> <user_name>
    # group replace <group_name> <file_path>

    def _dispatch_group(self, opts, args):
        client = self.system_client
        op = self._opt_arg_fail(args, 0, 'Group command not defined.')

        if op == 'list':
            print "Groups:"
            for group in client.group_list():
                print group
            return

        group_name = self._opt_arg_fail(args, 1, 'Group name not defined.')                    
        if op in ['create', 'delete']:        
            try:
                f = getattr(client, 'group_%s' % op)    
                f(group_name)
            except Unauthorized, e:
                sys.exit("Not allowed to %s groups - %s" % (op, str(e)))
            except Exception, e:
                sys.exit("Could %s group %s - %s" % (op, str(e)))

        elif op == 'retrieve':
            print "Users in %s: " % group_name
            
            try:
                for user in client.group_retrieve(group_name):
                    print user
            except Unauthorized, e:
                sys.exit("Not allowed to retrieve group contents - %s" % str(e))
            except Exception, e:
                sys.exit("Could not retrieve group %s - %s" % (group_name, str(e)))
        elif op == 'add':
            user_name = self._opt_arg_fail(args, 2, 'User name not defined.')

            try:
                users = client.group_retrieve(group_name)
                users.append(user_name)
                client.group_update(group_name, users=users)
            except Unauthorized, e:
                sys.exit("Not allowed to modify group contents - %s" % str(e))
            except Exception, e:
                sys.exit("Could add user to group %s - %s" % (group_name, str(e)))
        elif op == 'remove':
            try:
                users = client.group_retrieve(group_name)
            except Exception, e:
                sys.exit("Couldnt remove user from group - %s" % str(group_name))

            user_name = self._opt_arg_fail(args, 2, 'User name not defined.')            
            try:
                users.remove(user_name)
            except ValueError, e:
                self._error_msg('The given user, %s, was not in the group.' % user_name)
            try:
                client.group_update(group_name, users=users)
            except Unauthorized, e:
                sys.exit("Not allowed to modify group contents - %s" % str(e))
            except Exception, e:
                sys.exit("Could remove user from group %s - %s" % (group_name, str(e)))

        elif op == 'replace':
            try:
                f = getattr(client, 'group_update')        
                f(group_name, self._read_data(args[2]).splitlines())
            except Unauthorized, e:
                sys.exit("Not allowed to modify group contents - %s" % str(e))
            except Exception, e:
                sys.exit("Could remove modify group %s - %s" % (group_name, str(e)))
        else:
            self._error_msg('%s is not a valid group command.' % op)

    # index list
    # index recover <index_name>
    
    def _dispatch_index(self, opts, args):
        client = self.system_client
        op = self._opt_arg_fail(args, 0, 'Index command not defined.')

        if op == 'list':
            'Available indices:'
            for index in client.indices():
                print index
        elif op == 'recover':
            index_name = self._opt_arg_fail(args, 1, 'Index name not defined.')
            client.recover_index(index_name)
        else:
            self._error_msg('%s is not a valid index command.' % op)            
                    
def run(config_path='~/.stellaris/', args=None):

    if not args:
        args = sys.argv[1:]

    c = ConsoleClient(config_path)
    c.execute_command(args)

#    graph_client = GraphClient(cfg.service_url, base_path=cfg.base_path, graphs_prefix=cfg.prefix)
#    system_client = SystemClient(cfg.service_url, base_path=cfg.base_path, system_prefix=cfg.system_prefix)
#    query_client = QueryClient(cfg.service_url, index_name=index, base_path=cfg.base_path, query_prefix=cfg.query_prefix)
            

