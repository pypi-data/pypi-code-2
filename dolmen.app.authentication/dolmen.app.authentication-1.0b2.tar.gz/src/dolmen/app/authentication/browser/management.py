#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok

from dolmen import menu
from dolmen.app.authentication import ManageUsers, MF as _
from dolmen.app.layout import Index, Page, ContextualMenu, Edit
from dolmen.authentication import IPrincipalFolder
from dolmen.forms.base import Fields
from zeam.form.base.datamanager import makeAdaptiveDataManager

from zope.authentication.interfaces import IAuthentication
from zope.interface import Interface
from zope.schema import Tuple, Choice
from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class PrincipalFoldersList(grok.GlobalUtility):
    grok.name('dolmen.PAUPrincipalFolders')
    grok.implements(ISource, IVocabularyFactory)
    grok.provides(IVocabularyFactory)

    def __call__(self, pau):
        return SimpleVocabulary(
            [SimpleTerm(value=p.__name__, token=p.__name__,
                        title="%s (%s)" % (p.__name__, p.title or p.__name__))
             for p in pau.values() if IPrincipalFolder.providedBy(p)])


class IActiveFolders(Interface):
    """Principal folders management.
    """
    activeFolders = Tuple(
        title=_(u"Active authentication sources"),
        value_type=Choice(vocabulary='dolmen.PAUPrincipalFolders'),
        default=tuple())


class ActiveFoldersChoice(grok.Adapter):
    grok.implements(IActiveFolders)
    grok.context(IAuthentication)

    @apply
    def activeFolders():
        """Property allowing to access and set the active
        PrincipalFolders of the adapted PAU.
        """
        def fget(self):
            return tuple(
                (p for p in self.context.authenticatorPlugins
                 if IPrincipalFolder.providedBy(self.context.get(p))))

        def fset(self, values):
            auths = set(self.context.authenticatorPlugins)
            folders = set(
                (p.__name__ for p in self.context.values()
                 if IPrincipalFolder.providedBy(p)))

            self.context.authenticatorPlugins = (
                tuple(auths.difference(folders)) + values)

        return property(fget, fset)


@menu.menuentry(ContextualMenu, order=10)
class ManageAuth(Index):
    grok.context(IAuthentication)
    grok.require(ManageUsers)


@menu.menuentry(ContextualMenu, order=15)
class AuthSources(Page):
    grok.title(_("Authentication sources"))
    grok.context(IAuthentication)
    grok.require(ManageUsers)

    def update(self):
        self.folders = self.context.authenticatorPlugins
        self.credentials = self.context.credentialsPlugins


@menu.menuentry(ContextualMenu, order=20)
class PAUPreferences(Edit):
    grok.name('authenticators')
    grok.context(IAuthentication)
    grok.require(ManageUsers)

    fields = Fields(IActiveFolders)
    dataManager = makeAdaptiveDataManager(IActiveFolders)
    label = _(u"Edit the authentication sources")
