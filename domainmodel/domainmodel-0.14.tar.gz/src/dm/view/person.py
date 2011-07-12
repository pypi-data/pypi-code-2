from django.conf.urls.defaults import patterns
import dm.regexps

urlpatterns = patterns('',

    #
    ##  Person

    (r'^persons/create/(?P<returnPath>(.*))$',
        'person.create'),

    (r'^persons/pending/$',
        'person.pending'),

    (r'^persons/$',
        'person.list'),

    (r'^persons/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),

    (r'^persons/find/$',
        'person.search'),

    (r'^persons/search/$',
        'person.search'),

    (r'^persons/home/$',
        'person.read'),

    (r'^persons/(?P<personName>%s)/$' % dm.regexps.personName,
        'dm.view.person.read'),

    (r'^persons/(?P<personName>%s)/home/$' % dm.regexps.personName,
        'person.read'),

    (r'^persons/(?P<personName>%s)/update/$' % dm.regexps.personName,
        'person.update'),

    (r'^persons/(?P<personName>%s)/delete/$' % dm.regexps.personName,
        'person.delete'),

    (r'^persons/(?P<personName>%s)/approve/$' % dm.regexps.personName,
        'person.approve'),

)

