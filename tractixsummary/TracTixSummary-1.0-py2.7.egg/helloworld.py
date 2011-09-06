# -*- coding: UTF-8 -*-
'''
Created on Tue 16 Aug 2011

@author: leewei
'''
from trac.core import *
from trac.util.html import html
from trac.web import IRequestHandler
from trac.web.chrome import INavigationContributor
import os, sys

class TixSummaryPlugin(Component):
    """
        Barebones Trac plugin to display a metanav link to ticket summary.
    """
    implements(INavigationContributor, IRequestHandler)

    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        # set project defaults in trac.ini
        conf = self.env.config
        conf.set('header_logo', 'src', 'site/lshift-logo.png')

        conf.set('logging', 'log_level', 'DEBUG')
        conf.set('logging', 'log_type', 'file')

        conf.set('project', 'name', 'LShift')
        conf.set('project', 'url', 'http://www.lshift.net')
        conf.set('project', 'descr', 'Dev Trac instance')

        conf.set('trac', 'base_url', '/')
        conf.set('trac', 'debug_sql', 'yes')

        # consumer task init config options
        conf.set('traccron', 'ticker_enabled', True)
        conf.set('traccron', 'amqp_consumer.enabled', True)
        conf.set('traccron', 'amqp_consumer.cron', '0 0/1 * * * ?')
        conf.set('traccron', 'amqp_consumer.cron.enabled', True)
 
        conf.save()

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'a-ticket-summary'

    def get_navigation_items(self, req):
        yield ('metanav', 'a-ticket-summary',
            html.A('Ticket Summary', href=req.href.tixsummary()))

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == '/tixsummary'

    def process_request(self, req):
        return req.redirect(os.path.join(req.base_path,"report/12"))

