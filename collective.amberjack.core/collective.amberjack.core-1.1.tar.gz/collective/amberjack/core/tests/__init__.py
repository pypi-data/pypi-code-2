zcml_template = '''
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:collective.amberjack="http://namespaces.plone.org/collective.amberjack.core">
    
    %s
    
</configure>'''

DummyTour = {'tourId': u'dummy_id',
             'title': u'Dummy title',
             'steps': ({'url': u'/path',
                        'xpath': u'xpath expression',
                        'xcontent': u'xcontent',
                        'title': u'title',
                        'text': u'text',
                        'steps': ()},),
             }