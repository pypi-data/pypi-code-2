from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('plumi')

class IMemberMigrationConfiguration(Interface):
  """This interface defines the member migration configlet."""

  members_csv_file = schema.Bytes(title=_(u"Upload the Members CSV file."), required=True) 
  dry_run = schema.Bool(title=_(u"Dry run."), default=True)
  delete_existing_members = schema.Bool(title=_(u"Delete existing members."),default=False)

class IContentMigrationConfiguration(Interface):
  """This interface defines the content migration configlet."""

  content_archive_directory = schema.TextLine(title=_(u"The path to the directory where the content archive is contained."), required=True) 
  dry_run = schema.Bool(title=_(u"Dry run."), default=True)
  delete_existing_content = schema.Bool(title=_(u"Delete existing content."),default=False)
