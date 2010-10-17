# -*- coding: utf-8 -*-
# postcreate script. You could setup a workflow here for example

from cubes.calendar import WORKING_AM, WORKING_PM, WORKING, NON_WORKING

## DAY TYPES
dt_definitions = {u'journée de congés': NON_WORKING,
                  u'matinée de congés': WORKING_PM,
                  u'après-midi de congés': WORKING_AM,
                  u'journée de mat-paternité': NON_WORKING,
                  u'malade la journée': NON_WORKING,
                  u'malade le matin': WORKING_PM,
                  u"malade l'après-midi": WORKING_AM,
                  u'journée de grève': NON_WORKING,
                  u'matinée de grève': WORKING_PM,
                  u'après-midi de grève': WORKING_AM,
                  u'journée de travail': WORKING,
                  u'matinée de travail': WORKING_AM,
                  u'après-midi de travail': WORKING_PM,
                  u'non travaillé': NON_WORKING,
                  }

dt_store = {}
for dt_title, dt_type in dt_definitions.items():
    dt_store[dt_title] = create_entity('Daytype', title=dt_title, type=dt_type)

weekdays = []
## WEEK DAYS
for day in (u'monday', u'tuesday', u'wednesday', u'thursday', u'friday'):
    weekdays.append(create_entity('WeekDay', day_of_week=day,
                                  day_type=dt_store[u'journée de travail']))

for day in (u'saturday', u'sunday'):
    weekdays.append(create_entity('WeekDay', day_of_week=day,
                                  day_type=dt_store[u'non travaillé']))

## DEFAULT CALENDAR
defaultcal = create_entity('Calendar', title=u'Calendrier Francais')
defaultcal.set_relations(weekdays=weekdays, day_types=dt_store.values())

# Timeperiod workflow
wf = add_workflow('time-period workflow', 'Timeperiod')
tp_pending = wf.add_state(_('pending'), initial=True)
tp_validated  = wf.add_state(_('validated'))
wf.add_transition(_('validate'), tp_pending, tp_validated, ('managers',))
