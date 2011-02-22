# -*- coding: utf-8 -*-
""" Renders localization and execution code for jQuery Datepicker """

from zope.i18n import negotiate

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.controlpanel.calendar import ICalendarSchema


class DatepickerLocale(ViewletBase):
    """ Renders localization and execution code for jQuery Datepicker.
    """

    @property
    def language(self):
        return negotiate(self.request)

    def render(self):
        utool = getToolByName(self.context, "portal_url")
        ptool = getToolByName(self.context, "portal_properties")
        portal = utool.getPortalObject()
        first_day = ICalendarSchema(portal).firstweekday + 1
        future_years = ptool.site_properties.calendar_future_years_available
        return u"""\
    <script type="text/javascript">
    jQuery(function($) {
      if ($.datepick !== undefined) {
        var lt = String.fromCharCode(60),
            gt = String.fromCharCode(62),
        options = {
          yearRange: 'c-%s:c+%s', firstDay: %s,
          showTrigger: lt + 'button type="button" class="datepick"' + gt +
                       lt + 'img src="%s/popup_calendar.png" alt="" /' + gt +
                       lt + '/button' + gt
        };
        $.datepick.setDefaults($.datepick.regional['%s']);
        $(".date-widget, .datetime-widget").parent().datepick_z3cform(options);
        $(".overlay-ajax").bind("onLoad", function() {
          $(this).find(".date-widget, .datetime-widget")
            .parent().datepick_z3cform(options);
        });
      }
    });
    </script>
""" % (future_years * 5, future_years, first_day,
       portal.absolute_url(), self.language)
