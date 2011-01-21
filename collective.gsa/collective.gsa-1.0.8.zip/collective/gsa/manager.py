from logging import getLogger

from zope.interface import implements
from zope.component import getUtility, queryUtility

from collective.gsa.interfaces import IGSAConnectionConfig
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.gsa import GSAConnection
from collective.gsa.local import getLocal, setLocal

logger = getLogger('collective.gsa.manager')
marker = object()

class GSAConnectionManager(object):
    """ a thread-local connection manager for gsa """
    implements(IGSAConnectionManager)

    def getIndexConnection(self, timeout=marker):
        config = queryUtility(IGSAConnectionConfig)
        if not config:
            logger.error('Cannot resolve connection config. Not indexing')
            return None
            
        if not config.active:
            return None

        conn = getLocal('index_connection')
        if conn is None and config.host is not None:
            conn = GSAConnection(host=config.host, port=config.port_index, source=config.source, dual_site = config.dual_site)
            #setLocal('index_connection', conn)
            
        if conn is not None and timeout is not marker:
            conn.setTimeout(timeout)
        return conn

    def getSearchConnection(self, request, timeout=marker):
        isAnon = not request.cookies.get('GSACookie') and not request.get('__ac_name')
        config = queryUtility(IGSAConnectionConfig)
        if not config:
            logger.error('Cannot resolve connection config. Not searching')
            return None
        if not config.active:
            return None
        if config.host is not None:
            # if anonym search decide using public search config otherwise secure_search
            if isAnon:
                secure = config.public_search
            else:
                secure = config.secure_search

            port = secure and config.port_ssearch or config.port_psearch
            conn_string = 'search_connection_%s_%s' % (secure, port)
            
            conn = getLocal(conn_string)
            if conn is None:
                conn = GSAConnection(host=config.host, port = port, source=config.source, secure=secure, only_public = config.only_public, request = request)
                #setLocal(conn_string, conn)
                
        if conn is not None and timeout is not marker:
            conn.setTimeout(timeout)
        return conn
        
    def setIndexTimeout(self):
        """ set the timeout on the current (or to be opened) connection
            to the value specified for indexing operations """
        config = getUtility(IGSAConnectionConfig)
        conn = self.getIndexConnection()
        if conn is not None:
            conn.setTimeout(config.index_timeout)

    def setSearchTimeout(self):
        """ set the timeout on the current (or to be opened) connection
            to the value specified for search operations """
        config = getUtility(IGSAConnectionConfig)
        conn = self.getSearchConnection()
        if conn is not None:
            conn.setTimeout(config.search_timeout)
