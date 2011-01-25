# -*- coding: utf-8 -*-
"""hooks for the i18ncontent component

:organization: Logilab
:copyright: 2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

# from cubicweb.common.registerers import yes_registerer
# from cubicweb.server.hooksmanager import Hook
# from cubicweb.server.pool import PreCommitOperation

# class SetDefaultLangOp(PreCommitOperation):
#     def precommit_event(self):
#         if not self.entity.lang:
#             self.session.execute('SET X lang L WHERE L code "--", X eid %(x)s',
#                                  {'x': self.entity.eid}, 'x')
            
# class SetDefaultLangHook(Hook):
#     """set default language on translatable entities"""
#     # yes_registerer since the register_to method will set the hook for
#     # translatable entities (eg having the "lang" subject relation)
#     __registerer__ = yes_registerer
#     events = ('after_add_entity',)
    
#     @classmethod
#     def register_to(cls):
#         if not cls.enabled:
#             cls.warning('%s hook has been disabled', cls)
#             return
#         for ertype in cls.schema.rschema('lang').subjects():
#             for event in cls.events:
#                 yield event, ertype

#     def call(self, session, entity):
#         SetDefaultLangOp(session, entity=entity)

# XXX check that when lang relation or pivot_lang relation change,
# translation_of constraints are still fullfilled
