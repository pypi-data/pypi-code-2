from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class DownloadCSV(BrowserView):
    """ Download a CSV of all the providers
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.content = ''

    def write(self, csvrow):
        self.content = self.content + csvrow

    def __call__(self):
        providers = self.context.getProviders()
        self.request.RESPONSE.setHeader('Content-Type', 'text/csv')
        self.request.RESPONSE.setHeader('Content-Disposition',
                                        'attachment;filename=providers.csv')
        workflow_tool = getToolByName(self.context, 'portal_workflow')

        # header row
        header = '"Provider name","Provider contact name","Provider contact email","Sponsorship","Premium sponsorship","Employees","Firm Size","Annual Revenue","Workflow state"\n'
        self.write(header)

        for provider_brain in providers:
            provider = provider_brain.getObject()
            wfstate = workflow_tool.getInfoFor(provider, 'review_state', '')

            row = '"%s","%s","%s","%s","%s","%s","%s","%s","%s"\n' % (
                provider.pretty_title_or_id(),
                provider.getContactName(), provider.getContactEmail(),
                provider.isSponsor(), provider.isPremium(),
                provider.getEmployees(), provider.getCompanySize(),
                provider.getAnnualRevenues(), wfstate )
            self.write(row)

        return self.content
