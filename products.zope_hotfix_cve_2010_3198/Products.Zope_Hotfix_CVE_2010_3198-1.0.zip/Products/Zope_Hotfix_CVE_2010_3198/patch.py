import logging
LOG = logging.getLogger('ZServerPublisher')

def new_init(self, accept):
    from ZPublisher import publish_module
    try:
        from ZPublisher.WSGIPublisher import publish_module as publish_wsgi
        HAS_WSGI = True
    except ImportError:
        HAS_WSGI = False
    while 1:
        try:
            name, a, b=accept()
            if name == "Zope2":
                try:
                    publish_module(
                        name,
                        request=a,
                        response=b)
                finally:
                    b._finish()
                    a=b=None

            elif HAS_WSGI and name == "Zope2WSGI":
                try:
                    res = publish_wsgi(a, b)
                    for r in res:
                        a['wsgi.output'].write(r)
                finally:
                    # TODO: Support keeping connections open.
                    a['wsgi.output']._close = 1
                    a['wsgi.output'].close()
        except:
            LOG.error('exception caught', exc_info=True)

from ZServer.PubCore.ZServerPublisher import ZServerPublisher
ZServerPublisher.__init__ = new_init
