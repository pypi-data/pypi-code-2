from Products.Archetypes import atapi
from Products.ATContentTypes.content import link

class Redirect(link.ATLink):

    meta_type = portal_type = archetype_name = 'Redirect'

    schema = link.ATLink.schema.copy()
    schema.addField(
        atapi.StringField('localPath',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(
            description='The portal rooted path to redirect',
            label=u'Local Path')))
    schema.moveField('localPath', before='remoteUrl')

atapi.registerType(Redirect, 'collective.redirect')
