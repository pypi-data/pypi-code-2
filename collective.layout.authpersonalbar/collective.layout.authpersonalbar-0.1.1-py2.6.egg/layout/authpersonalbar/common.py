from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class PersonalBarHolderViewlet(ViewletBase):
    """Don't show the viewlet to anon users.
    """
    index = ViewPageTemplateFile('personal_bar_holder.pt')

    def update(self):
        super(PersonalBarHolderViewlet, self).update()
        self.anonymous = self.portal_state.anonymous()
