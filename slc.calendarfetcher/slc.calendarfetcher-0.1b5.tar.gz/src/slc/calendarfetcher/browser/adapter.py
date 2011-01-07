import os
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from slc.calendarfetcher.browser.calendarfetcher import FetcherConfigView

form_adapter = ZopeTwoFormTemplateFactory(
        os.path.join(os.path.dirname(__file__), 'templates/configform.pt'),
        form=FetcherConfigView
        )
