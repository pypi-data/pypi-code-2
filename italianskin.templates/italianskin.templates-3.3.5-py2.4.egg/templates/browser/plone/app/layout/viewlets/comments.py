from plone.app.layout.viewlets.comments import CommentsViewlet as OriginalCommentsViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CommentsViewlet(OriginalCommentsViewlet):
    render = ViewPageTemplateFile('comments.pt')


