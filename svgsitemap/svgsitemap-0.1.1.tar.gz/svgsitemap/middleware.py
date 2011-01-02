"""
request dispatcher
"""

__all__ = ['MapserverMiddleware', 'SVGSiteMap']

import os
import urlparse
from fnmatch import fnmatch
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
                 'minwidth': '0.1',
                 'maxlength': 60,
                 'excluded': '*.css *.js */static/* /css/* *.ico /backgrounds/* *.png *.jpg',

                 # input/output
                 'file': None, # graphviz file
                 'output': None, # .svg file

                 # graph attributes
                 'bgcolor': 'black',
                 'fontcolor': 'white',
                 'fontname': 'Helvetica',
                 'fontsize': '80.0',
                 'nodecolor': 'aqua',
                 'edgecolor': 'lime',
                 'shape': 'plaintext',
                 'len': '1.0',
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
        if isinstance(self.excluded, basestring):
            self.excluded = self.excluded.split()
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
                if self.exclude(edge[0], edge[1]):
                    self.graph.remove_edge(edge[0], edge[1])
                    continue
                if edge.attr['tooltip']:
                    count = int(edge.attr['tooltip'].split(':', 1)[0].strip())
                else:
                    label = edge.attr['label']
                    count = int(label)
                    self.label(edge, count)
                self.edges[(edge[0], edge[1])] = count
                if count > self.max:
                    self.max = count
            self.remove_orphans()
            self.set_widths()
        else:
            self.graph = AGraph(name=self.name, splines=False, directed=True)

        # make it pretty
        self.graph.graph_attr['name'] = self.name
        self.graph.graph_attr['label'] = self.name
        self.graph.graph_attr['fontname'] = self.fontname
        self.graph.graph_attr['fontcolor'] = self.fontcolor
        self.graph.graph_attr['bgcolor'] = self.bgcolor
        self.graph.graph_attr['overlap'] = 'false'
        self.graph.graph_attr['sep'] = '0'
        self.graph.node_attr['color'] = self.nodecolor
        self.graph.node_attr['fontcolor'] = self.fontcolor
        self.graph.node_attr['fontname'] = self.fontname
        self.graph.node_attr['fontsize'] = self.fontsize
        self.graph.node_attr['shape'] = self.shape
        self.graph.edge_attr['color'] = self.edgecolor
        self.graph.edge_attr['fontcolor'] = self.fontcolor
        self.graph.edge_attr['fontname'] = self.fontname
        self.graph.edge_attr['fontsize'] = self.fontsize
        self.graph.edge_attr['len'] = self.len
        self.graph.edge_attr['arrowsize'] = self.arrowsize

        if self.edges:
            self.save()
        
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
        if self.exclude(from_url, to_url):
            return # ignore certain urls
        
        if (from_url, to_url) in self.edges:
            count = self.edges[(from_url, to_url)]
            count += 1
            if count > self.max:
                self.max = count
            self.edges[(from_url, to_url)] = count
            edge = self.graph.get_edge(from_url, to_url)
            self.label(edge, count)
        else:
            self.edges[(from_url, to_url)] = 1
            self.max = 1
            labeltooltip = '1: %s -> %s' % (from_url, to_url)
            self.graph.add_edge(from_url, to_url, label='', tooltip=labeltooltip, href='#')

        if self.maxwidth:
            self.set_widths()

        for url in from_url, to_url:
            node = self.graph.get_node(url)
            node.attr['label'] = url
            node.attr['href'] = url

        self.save()

    def label(self, edge, count):
        edge.attr['label'] = ''
        edge.attr['tooltip'] = '%d: %s -> %s' % (count, edge[0], edge[1])
        edge.attr['labeltooltip'] = edge.attr['tooltip']
        edge.attr['href'] = '#'

    def exclude(self, *urls):
        """tell whether the edge is excluded"""
        for pattern in self.excluded:
            for url in urls:
                if fnmatch(url, pattern):
                    return True
        for url in urls:
            if len(url) > self.maxlength:
                return True
        return False

    def set_widths(self):
        if self.maxwidth:
            for edge in self.graph.edges():
                count = self.edges[(edge[0], edge[1])]
                width = self.maxwidth * count / self.max
                if not width:
                    width = self.minwidth
                edge.attr['style'] = 'setlinewidth(%s)' % width

        else:
            for edge in self.graph.edges():
                edge.attr['style'] = ''

    def save(self):
        if self.file:
            self.graph.write(self.file)
        if self.output:
            self.graph.draw(self.output, prog='neato')

    def remove_orphans(self):
        flag = True
        while flag:
            flag = False
            for node in self.graph.nodes():
                if not self.graph.neighbors(node) or self.exclude(node):
                    flag = True
                    self.graph.remove_node(node)
