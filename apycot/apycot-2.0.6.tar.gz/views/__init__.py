'''apycot reports'''

_ = unicode

import re

from cubicweb.view import NOINDEX, NOFOLLOW
from cubicweb.web import uicfg, formwidgets as wdgs
from cubicweb.web.views import urlpublishing
from cubicweb.web.views.urlrewrite import rgx, build_rset, SchemaBasedRewriter, \
                                          SimpleReqRewriter

from cubes.narval.proxy import bot_proxy

def anchor_name(data):
    """escapes XML/HTML forbidden characters in attributes and PCDATA"""
    return (data.replace('&', '').replace('<', '').replace('>','')
            .replace('"', '').replace("'", ''))

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs

# ui configuration #############################################################


# register generated message id
_('Available checkers:')
_('Available options:')

def build_help_func(apycot_type):
    def help_func(form, field, apycot_type=apycot_type):
        attr = field.name
        etype = form.edited_entity.__regid__
        req = form._cw
        help = req.vreg.schema.eschema(etype).rdef(attr).description
        help = '<div>%s.</div>' % req._(help)
        try:
            # ProtocolError may be called during method() call
            bot = bot_proxy(req.vreg.config, req.data)
            method = getattr(bot, 'available_%s' % apycot_type)
            available = ', '.join(defdict.get('id', defdict.get('name'))
                                  for defdict in method())
        except Exception, ex:
            form.warning('cant contact apycot bot: %s', ex)
            return help
        help += '<div>%s %s (<a href="%s">%s</a>)</div>' % (
            req.__('Available %s:' % apycot_type), available,
            req.build_url('apycotdoc#%s' % apycot_type),
            req._('more information')
            )
        return help
    return help_func

for etype in ('TestConfig', 'ProjectEnvironment'):
    _afs.tag_subject_of((etype, 'refinement_of', '*'), 'main', 'attributes')
    helpfunc = build_help_func('options')
    _affk.tag_attribute((etype, 'check_config'), {'help': helpfunc})


_affk.tag_attribute(('ProjectEnvironment', 'vcs_path'),
                    {'widget': wdgs.TextInput})
_afs.tag_subject_of(('ProjectEnvironment', 'local_repository', '*'), 'main', 'inlined')
_afs.tag_object_of(('*', 'for_environment', 'ProjectEnvironment'), 'main', 'relations')

_affk.tag_attribute(('TestConfig', 'start_mode'), {'sort': False})
_affk.tag_attribute(('TestConfig', 'start_rev_deps'),
                    {'allow_none': True,
                     'choices': [(_('inherited'), ''), ('yes', '1'), ('no', '0')]})
_affk.tag_attribute(('TestConfig', 'subpath'),
                    {'widget': wdgs.TextInput})
_afs.tag_attribute(('TestConfig', 'computed_start_mode'), 'main', 'hidden')

_afs.tag_subject_of(('TestConfig', 'use_recipe', '*'), 'main', 'attributes')


_abba = uicfg.actionbox_appearsin_addmenu
_abba.tag_subject_of(('*', 'has_apycot_environment', '*'), True)
_abba.tag_subject_of(('*', 'local_repository', '*'), False) # inlined form
_abba.tag_object_of(('*', 'for_check', '*'), False)
_abba.tag_object_of(('*', 'during_execution', '*'), False)
_abba.tag_object_of(('*', 'using_config', '*'), False)
_abba.tag_object_of(('*', 'using_environment', '*'), False)
_abba.tag_object_of(('*', 'on_environment', '*'), False)


# urls configuration ###########################################################

class SimpleReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/apycotdoc'), dict(vid='apycotdoc')),
        ]

# XXX necessary since it takes precedence other a /testexecution/' rule above
class RestPathEvaluator(urlpublishing.RestPathEvaluator):

    def handle_etype(self, req, cls):
        if cls.__regid__ == 'TestExecution':
            # XXX query duplicated from TESummaryTable
            rset = req.execute(
                    'Any T,PE,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
                    'T status TS, T using_config TC, T using_environment PE, '
                    'T branch TB, T starttime TST, T endtime TET, T log_file TF?')
            req.form['displayfilter'] = ''
            req.form['vid'] = 'apycot.te.summarytable'
            return None, rset
        return super(RestPathEvaluator, self).handle_etype(req, cls)

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (RestPathEvaluator,))
    vreg.register_and_replace(RestPathEvaluator, urlpublishing.RestPathEvaluator)
