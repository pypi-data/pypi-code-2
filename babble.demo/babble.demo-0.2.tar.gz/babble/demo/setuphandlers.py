import logging
from Products.CMFCore.utils import getToolByName

log = logging.getLogger('babble.demo/setuphandlers.py')

def add_chat_service(context):
    if context.readDataFile("babble.demo_marker.txt") is None:
        return

    root = context.getSite().aq_parent
    view = root.unrestrictedTraverse('+/addChatService.html')
    view(add_input_name='chatservice', title='Chat Service', submit_add=1)


def configure_chat_tool(context):
    """ Configure the chat_service to point to the correct URL"""
    if context.readDataFile("babble.demo_marker.txt") is None:
        return

    site = context.getSite()
    portal_chat = getToolByName(site, 'portal_chat')
    portal_chat._updateProperty('name', 'chatservice')
    portal_chat._updateProperty('host', 'localhost')
    portal_chat._updateProperty('port', '8081')
    portal_chat._updateProperty('username', 'admin')
    portal_chat._updateProperty('password', 'admin')


