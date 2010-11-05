from zope.component import getSiteManager
from zope.component import queryUtility
from zope.i18n.translationdomain import TranslationDomain
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.testmessagecatalog import TestMessageCatalog
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog

from pythongettext.msgfmt import Msgfmt
import os

def handler(catalogs, name):
    """ special handler handling the merging of two message catalogs """
    gsm = getSiteManager()
    # Try to get an existing domain and add the given catalogs to it
    domain = queryUtility(ITranslationDomain, name)
    if domain is None:
        domain = TranslationDomain(name)
        gsm.registerUtility(domain, ITranslationDomain, name=name)
    for catalog in catalogs:
        domain.addCatalog(catalog)
    # make sure we have a TEST catalog for each domain:
    domain.addCatalog(TestMessageCatalog(name))

def compile(conf, domain, lang):
    path = os.path.join(os.environ.get('INSTANCE_HOME'), 'var/amberjack_i18n')
    path = os.path.normpath(path)
    if not os.path.isdir(path):
        os.makedirs(path)

    filename = '%s-%s' % (lang, os.path.basename(conf.name))

    po = open(os.path.join(path, filename), 'w')
    po.write(conf.read())
    po.close()
    po = open(po.name, 'r')
    _mo = Msgfmt(po, domain).getAsFile()
    mo = open(os.path.join(path, filename.replace('.po','.mo')), 'wb')
    mo.write(_mo.read())
    mo.close()
    _mo.close()
    return str(mo.name)

def registerTranslations(conf):
    path, filename = os.path.split(conf.name)
    path, lang = os.path.split(os.path.dirname(conf.name))
    domain, ext = filename.split('.po')
    domain = str(domain)
    catalogs = [GettextMessageCatalog(lang, domain, compile(conf,domain, lang))]
    handler(catalogs, domain)
