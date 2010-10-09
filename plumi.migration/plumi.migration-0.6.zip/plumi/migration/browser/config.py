import logging

from zope.formlib import form
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName   

from plone.app.controlpanel.form import ControlPanelForm

from plumi.migration.interfaces.migration import IMemberMigrationConfiguration, IContentMigrationConfiguration
from plumi.migration.members_csv import import_members_csv

_ = MessageFactory('plumi')

class MemberMigrationConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IMemberMigrationConfiguration)
    label = _(u"Member migration.")
    description = _(u"Importing members from Plumi 0.2.x sites.")
    form_name = _(u"Upload a exported set of Members using CSV")

    @form.action(_(u'Import Members'))
    def handle_add(self,action,data):
        log=getLogger()
        log.debug("handle_add has data %s " % data)
        util = member_form_adapter(self.context)
        util.members_csv_file = data['members_csv_file']
        util.dry_run = data['dry_run']
        util.delete_existing_members = data['delete_existing_members']

        #do the import. the method will find the configuration class using the utility lookup on the context
        status_csv = import_members_csv(self.context) 
        self.status = _(u'Successfully imported.') + ' ' + status_csv
  

class MemberMigrationConfiguration(SimpleItem):
    implements(IMemberMigrationConfiguration)
        
    members_csv_file = FieldProperty(IMemberMigrationConfiguration['members_csv_file'])
    dry_run = FieldProperty(IMemberMigrationConfiguration['dry_run'])
    delete_existing_members = FieldProperty(IMemberMigrationConfiguration['delete_existing_members'])

def getLogger():
    return logging.getLogger('plumi.migration')

def member_form_adapter(context):
    return getUtility(IMemberMigrationConfiguration, name='member_migration_config', context=context)


class ContentMigrationConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IContentMigrationConfiguration)
    label = _(u"Content migration.")
    description = _(u"Importing content from Plumi 0.2.x sites.")
    form_name = _(u"Import content from the server.")

    @form.action(_(u'Import Content'))
    def handle_add(self,action,data):
        log=getLogger()
        log.debug("handle_add has data %s " % data)
        status_content = ''
        util = content_form_adapter(self.context)

        util.content_archive_directory = data['content_archive_directory']
        util.dry_run = data['dry_run']
        util.delete_existing_content = data['delete_existing_content']

        log.info('importin from %s ' % util.content_archive_directory)

        #get the portal_json_migrator tool
        json_mt = getToolByName(self.context, 'portal_json_migrator') 
        old_targetfolder = json_mt.targetfolder
        json_mt.targetfolder = util.content_archive_directory
        #do the import. the method will find the configuration class using the utility lookup on the context
        if not util.dry_run:
            json_mt.importObjects(overwrite=util.delete_existing_content)
            #status_content = ' imported %s items ' % json_mt.n_items
            self.status = _(u'Successfully imported.') 

        #reset targetfolder
        json_mt.targetfolder = old_targetfolder
  

class ContentMigrationConfiguration(SimpleItem):
    implements(IContentMigrationConfiguration)
        
    content_archive_directory = FieldProperty(IContentMigrationConfiguration['content_archive_directory'])
    dry_run = FieldProperty(IContentMigrationConfiguration['dry_run'])
    delete_existing_content = FieldProperty(IContentMigrationConfiguration['delete_existing_content'])

def content_form_adapter(context):
    return getUtility(IContentMigrationConfiguration, name='content_migration_config', context=context)
