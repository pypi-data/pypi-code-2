"""
request dispatcher
"""

__all__ = ['MapserverMiddleware', 'SVGSiteMap']

import os
import urlparse
from pygraphviz import AGraph
from webob import Request, Response, exc

class MapserverMiddleware(object):
    """silly middleware to serve just the svg"""
    def __init__(self, app, svgmap, path='/map'):
        self.app = app
        self.svgmap = svgmap
        self.path = path

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.path_info == self.path or not self.path:
            if not os.path.exists(self.svgmap):
                res = exc.HTTPNotFound()
                return res(environ, start_response)
            content = file(self.svgmap).read()
            res = Response(content_type='image/svg+xml', body=content)
            return res(environ, start_response)
        return self.app(environ, start_response)
    

class SVGSiteMap(object):

    ### class level variables
    defaults = { 'name': '',
                 'hosts': '',
                 'external_referers': True,
                 'maxwidth': 5,
                 'minwidth': '0.01',

                 # input/output
                 'file': None, # .ini file
                 'output': None, # .svg file

                 # graph attributes
                 'bgcolor': 'black',
                 'fontcolor': 'white',
                 'fontname': 'Helvetica',
                 'fontsize': '10.0',
                 'nodecolor': 'aqua',
                 'edgecolor': 'lime',
                 'shape': 'box',
                 'len': '1.3',
                 'arrowsize': '0.5',
                 }

    def __init__(self, app, **kw):

        # boilerplate
        self.app = app
        self.edges = {}
        self.max = 0

        # set attrs from defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # sanity checks + data fixing
        assert self.output, "Please give an output file"
        assert self.file, "Cannot save file!"
        self.maxwidth = float(self.maxwidth)
        if self.hosts:
            self.hosts = self.hosts.split()
        else:
            self.hosts = []
        if isinstance(self.external_referers, basestring):
            self.external_referers = self.external_referers.lower() == 'true'

        # open the graph
        if os.path.exists(self.file):
            self.graph = AGraph(self.file, name=self.name, splines=False, directed=True)
            for edge in self.graph.edges():
                count = int(edge.attr['label'])
                self.edges[(edge[0], edge[1])] = count
                if count > self.max:
                    self.max = count
        else:
            self.graph = AGraph(name=self.name, splines=False, directed=True)

        # make it pretty
        self.graph.graph_attr['name'] = self.name
        self.graph.graph_attr['label'] = self.name
        self.graph.graph_attr['fontname'] = self.fontname
        self.graph.graph_attr['fontcolor'] = self.fontcolor
        self.graph.graph_attr['bgcolor'] = self.bgcolor
        self.graph.node_attr['color'] = self.nodecolor
        self.graph.node_attr['fontcolor'] = self.fontcolor
        self.graph.node_attr['fontname'] = self.fontname
        self.graph.node_attr['fontsize'] = self.fontsize
        self.graph.node_attr['shape'] = self.shape
        self.graph.node_attr['width'] = '0.1'
        self.graph.node_attr['height'] = '0.1'
        self.graph.edge_attr['color'] = self.edgecolor
        self.graph.edge_attr['fontcolor'] = self.fontcolor
        self.graph.edge_attr['fontname'] = self.fontname
        self.graph.edge_attr['fontsize'] = self.fontsize
        self.graph.edge_attr['len'] = self.len
        self.graph.edge_attr['arrowsize'] = self.arrowsize
        
    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.referer:

            # parse the URLs
            parsed_referer = urlparse.urlsplit(request.referer)
            parsed_referee = urlparse.urlsplit(request.url)
            islocal = False

            # see if its local or not
            localhosts = self.hosts[:]
            if parsed_referee.hostname not in localhosts:
                localhosts.append(parsed_referee.hostname)
            for host in localhosts:
                if parsed_referer.hostname == host or parsed_referer.hostname.endswith('.' + host):
                    islocal = True
                break

            # make the connection
            if islocal:
                self.add(parsed_referer.path, parsed_referee.path)
            else:
                if self.external_referers:
                    self.add(request.referer, parsed_referee.path)
                    
        return self.app(environ, start_response)

    def add(self, from_url, to_url):
        """add a conncection in the graph"""

        if from_url == to_url:
            return # don't do self-references
        
        if (from_url, to_url) in self.edges:
            count = self.edges[(from_url, to_url)]
            count += 1
            if count > self.max:
                self.max = count
            self.edges[(from_url, to_url)] = count
            edge = self.graph.get_edge(from_url, to_url)
            edge.attr['label'] =  str(count)
        else:
            self.edges[(from_url, to_url)] = 1
            self.max = 1
            self.graph.add_edge(from_url, to_url, label='1')

        for edge in self.graph.edges():
            count = self.edges[(edge[0], edge[1])]
            width = self.maxwidth * count / self.max
            if not width:
                width = self.minwidth
            edge.attr['style'] = 'setlinewidth(%s)' % width

        for url in from_url, to_url:
            node = self.graph.get_node(url)
            node.attr['label'] = url
            node.attr['href'] = url

        if self.file:
            self.graph.write(self.file)
        if self.output:
            self.graph.draw(self.output, prog='neato')
