from zope import interface, schema

class IDemoContent(interface.Interface):

    country = schema.Choice(title=u'Country',
                            vocabulary='autocomplete.demo.countries')
    
    
