# generate Subjects

import yql
from calais import Calais
from silcc import Silcc
from tagthenet import TagTheNet

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.taghelper.interfaces import ITagHelperSettingsSchema




PREFERRED_ENTITIES = ['City', 'Continent', 'Country', 'MedicalCondition',
    'MedicalTreatment', 'NaturalFeature', 'Organization', 'ProvinceOrState',
    'Region', 'IndustryTerm']
PREFERRED_FACTS = ['EnvironmentalIssue', 'ManMadeDisaster', 'NaturalDisaster']

def get_yql_subjects(url):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.yahoo_api_key
    if api_key:
        y = yql.Public(api_key)
        query = '''select * from search.termextract where context in (
                select content from html where url="%s"
                )''' % url
        try:
            result = y.execute(query)
        except:
            return []
        return result.rows
    else:
        return []

def get_ttn_subjects(text):
    ttn = TagTheNet()
    return ttn.analyze(text)

def get_ttn_subjects_remote(url):
    ttn = TagTheNet()
    return ttn.analyze_url(url)


def get_silcc_subjects(text):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.silcc_api_key
    if api_key == None:
        api_key=''
    url  = settings.silcc_url
    silcc = Silcc(api_key, url)
    try:
        return silcc.execute(text)
    except:
        return []

def get_calais_subjects(text, uid):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.calais_api_key
    subjects=[]
    if api_key:
        calais = Calais(api_key)
        try:
            result = calais.analyze(text, external_id = uid)
        except:
            return []
        if hasattr( result, 'entities'):
            for entity in result.entities:
                if entity['_type'] in PREFERRED_ENTITIES:
                    subjects.append(entity['name'])
        if hasattr( result, 'socialTag'):
            for tag in result.socialTag:
                subjects.append(tag['name'])
        if hasattr( result, 'relations'):
            for fact in result.relations:
                if fact['_type'] in PREFERRED_FACTS:
                    ft = fact.get(fact['_type'].lower())
                    if ft:
                        subjects.append(ft)
    return subjects
