"""
.. autoclass:: Xapian
"""
from ordf.handler import HandlerPlugin
import pkg_resources
import xapian

class Xapian(HandlerPlugin):
    """
    When adding/replacing a graph in the database we use an application 
    specific function to actually create the indexed document. This will
    look in entrypoints of the form::

        [ordf.xapian]
        index = myapp.lib.xapindex:index_graph
        search = myapp.lib.xapindex:search

    :meth:`index_graph` takes a graph and returns a *(docid,
    :class:`xapian.Document`)* tuple.

    For searching, we use another application specific function,
    :meth:search which takes a xapian database connector, query string,
    limit and offset arguments. The result format should be the as 
    returned from :meth:`xapian.Enquire.get_mset`.

    In order to support more than one indexer this class may be passed a
    key-word argument "name" in the constructor to override the key in
    the configuration section.

    .. automethod:: open
    """
    def __init__(self, server, name="index"):
        self.host, port = server.split(":")
        self.port = int(port)
        self.name = name
        self.db = None

    def open(self, writeable=False):
        """
        Slightly complicated routine that allows us to open a connection to
        a xapian database running on a TCP port and cache the handle fo 
        future use. Default is to open read-only.
        """
        if isinstance(self.db, xapian.Database):
            ## we have an open database. tree possibilities
            ## 1. we need a writeable one and we have a read-only one
            if writeable and not isinstance(self.db, xapian.WritableDatabase):
                self.db.close()
            ## 2. we have a writeable one and we need a read-only one
            elif not writeable and isinstance(self.db, xapian.WritableDatabase):
                self.db.close()
            ## 3. we have just the right kind of database, check that it is
            ##    still good
            else:
                try:
                    self.db.reopen()
                    return self.db
                except xapian.NetworkError:
                    pass
        ## either we have no database at this point or we have just closed
        ## the one we had which turned out to be the wrong type
        if writeable:
            self.db = xapian.remote_open_writable(self.host, self.port)
        else:
            self.db = xapian.remote_open(self.host, self.port)
        return self.db

    def close(self):
        if isinstance(self.db, xapian.Database):
            self.db.close()
            self.db = None

    def put(self, store):
        """
        """
        for entrypoint in pkg_resources.iter_entry_points(group="ordf.xapian"):
            if entrypoint.name == self.name:
                index = entrypoint.load()
                db = self.open(writeable=True)
                for docid, doc in index(store):
                    db.replace_document(docid, doc)
                db.flush()
                return
        raise ImportError("no plugin in [ordf.xapian] named %s" % self.name)
