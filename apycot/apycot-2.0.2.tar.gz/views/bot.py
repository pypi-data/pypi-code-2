"""this module contains views related to bot status and activity

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.view import StartupView

from cubes.narval.proxy import bot_proxy

class ApycotHelpView(StartupView):
    __regid__ = 'apycotdoc'

    def page_title(self):
        return self._cw._('apycot documentation')

    def call(self):
        _ = self._cw._
        self.w(u'<h1>%s</h1>' % self.page_title())
        bot = bot_proxy(self._cw.vreg.config, self._cw.data)
        self.w(u'<p>%s</p>' % _(
            'First notice that you may miss some information if you\'re using '
            'some plugin not loaded by the apycot bot.'))
        self.section('checkers')
        headers = [_('checker'), _('need preprocessor'), _('description')]
        data = [(defdict['id'], defdict['preprocessor'], xml_escape(defdict['help']))
                 for defdict in bot.available_checkers()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)
        self.section('preprocessors')
        headers = [_('preprocessor'), _('description')]
        data = [(defdict['id'], xml_escape(defdict['help']))
                 for defdict in bot.available_preprocessors()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)
        self.section('options')
        headers = [_('option'), _('required'), _('type'), _('description')]
        data = [(defdict.get('id', defdict['name']),
                 defdict.get('required') and _('yes') or _('no'),
                 defdict['type'], xml_escape(defdict['help']))
                 for defdict in bot.available_options()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)

    def section(self, name):
        self.w(u'<h2>%s</h2><a name="%s"/>' % (self._cw._(name), name))


