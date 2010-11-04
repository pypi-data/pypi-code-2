# -*- coding: utf-8 -*-

from megrok.nozodb.utils import config, NOZODBWSGIPublisherApplication


def nozodb_factory(global_conf, **local_conf):
    """ this factory creates an wsgi-application, which don't
        have a releation to zodb
    """
    zope_conf = global_conf['zope_conf']
    config(zope_conf)
    app = NOZODBWSGIPublisherApplication(handle_errors=True)
    return app
