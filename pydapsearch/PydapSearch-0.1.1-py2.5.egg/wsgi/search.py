import os

from webob import Request, Response
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from httplib2 import Http
from simplejson import dumps
from lxml import etree

from pydap.client import open_url
from pydap.lib import walk
from pydap.model import *


def make_middleware(app, global_conf, **kwargs):
    return SearchMiddleware(app, global_conf=global_conf, **kwargs)


class SearchMiddleware(object):
    def __init__(self, app, catalog, index='index', **kwargs):
        self.app = app
        self.catalog = catalog
        self.indexdir = index
        self.indexed = False

    def __call__(self, environ, start_response):
        # force an indexation at first request
        if not self.indexed:
            self.indexed = True
            self._index()

        environ['pydap.search'] = True
        req = Request(environ)        
        if req.path_info == '/_index':
            # regenerate index
            self._index()
            res = Response(body='', status='204 No Content')
        elif req.path_info == '/' and 'q' in req.params:
            # do the search
            parser = QueryParser('content', schema=self.schema)
            q = req.params.getone('q')
            query = parser.parse( q.decode('utf-8') )
            searcher = self.index.searcher()
            page = int(req.params.get('pw', 1))
            results = searcher.search_page(query, page)

            output = {
                    'offset': results.offset,
                    'pagecount': results.pagecount,
                    'pagenum': results.pagenum,
                    'pagelen': results.pagelen,
                    'total': results.total,
                    'results': list(results),
                    }
            if results.pagecount > results.pagenum:
                output['next'] = '%s?q=%s&pw=%s' % (req.path_url, q, page+1)
            if page > 1:
                output['previous'] = '%s?q=%s&pw=%s' % (req.path_url, q, page-1)

            res = Response(
                    body=dumps(output),
                    content_type='application/json',
                    charset='utf-8')
        else:
            # return unmodified response
            res = req.get_response(self.app)

        return res(environ, start_response)

    def _index(self):
        self.schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
        if not os.path.exists(self.indexdir):
            os.mkdir(self.indexdir)
        self.index = create_in(self.indexdir, self.schema)

        # request the catalog.xml file from the application
        writer = self.index.writer()
        for url in crawl(self.catalog):
            try:
                dataset = open_url(url)
            except:
                continue

            try:
                _title = dataset.attributes['NC_GLOBAL']['title']
            except:
                _title = dataset.name

            # index each variable
            for var in walk(dataset):
                if isinstance(var, DatasetType):
                    title = _title
                    path = '%s.html' % url
                else:
                    name = var.attributes.get('long_name', var.name)
                    title = '%s @ %s' % (name, _title)
                    path = '%s.html?%s' % (url, var.id)
                
                content = ' '.join(get_attributes(var))
                writer.add_document(
                        title=title.decode('utf-8'),
                        path=path.decode('utf-8'),
                        content=content.decode('utf-8'))
        writer.commit()


def crawl(catalog):
    """Grab all URLs from a THREDDS catalog."""
    resp, content = Http().request(catalog)
    xml = etree.fromstring(content)
    for dataset in xml.iterfind('.//{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}dataset[@urlPath]'):
        yield dataset.attrib['urlPath']
    for subdir in xml.iterfind('.//{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}catalogRef'):
        for url in crawl(subdir.attrib['{http://www.w3.org/1999/xlink}href']):
            yield url 


def get_attributes(container):
    """Get all attribute values from a Pydap dataset."""
    values = []

    def append(d):
        for k, v in d.items():
            if isinstance(v, dict):
                append(v)
            else:
                values.append( str(v) )

    for var in walk(container):
        append(var.attributes)

    return values


if __name__ == '__main__':
    from paste.deploy import loadapp
    app = SearchMiddleware( loadapp('config:/Users/roberto/tmp/pydap/server.ini'), 'http://localhost:8080/catalog.xml' )
    from paste.httpserver import serve
    serve(app)
