from Acquisition import aq_inner

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFPlone.utils import normalizeString, safe_unicode


class SelectionPropertyTypeVocabulary(object):
    """Returns list of items returned by select_variable
    collable set into selection property type.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
      """Here we get Selection Property Type as context with set
      select_variable to call for list of items in vocabulary.
      """
      select_variable = context.select_variable
      context = aq_inner(context.context)
      if select_variable and hasattr(context, select_variable):
          values = getattr(context, select_variable)
          if callable(values):
              try:
                  values = values()
              except Exception:
                  return SimpleVocabulary([])
      else:
          return SimpleVocabulary([])
          
      # make sure our vocabulary returns only unicode strings so that
      # selection widget doesn't break with decoding error during render
      result = []
      for v in values:
          if isinstance(v, str):
              v = v.decode('utf-8')
          elif not isinstance(v, str):
              v = safe_unicode(str(v))
          
          # we also need to strip out every term in order to be compliant with
          # IPropertyManager interface
          v = v.strip()
          
          # we use custom widget so this token is not use in template,
          # only in widget converter
          token = normalizeString(v, encoding='utf-8')
          
          result.append(SimpleTerm(v, token, v))
      
      return SimpleVocabulary(result)
