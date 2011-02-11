# -*- coding: utf-8 -*-

#delete after the person's cube migration
add_entity_type('PostalAddress')

if confirm('backport person address?'):
    for person_eid, address, description in rql(
        'Any X,XA,XD WHERE X is Person, NOT X address NULL, X address XA, X description XD'):
        ## move address to description if it's longer than 256 character
        if len(address) < 256:
            rql('INSERT PostalAddress P: '
                'P street %(street)s , P city %(city)s, P postalcode %(pc)s, D postal_address P '
                'WHERE D is Person, D eid %(eid)s',
                {'street':address, 'city':u'???', 'pc':u'???', 'eid': person_eid},
                ask_confirm=False)
        else:
            if description:
                description = description + ' ' + address
            else:
                description = address
            rql("SET X description %(D)s WHERE X is Person, X eid %(eid)s",
                {'D': description, 'eid':person_eid})
    checkpoint()

add_entity_type('Application')

if confirm('add application wf?'):
    ##add state and transition on Apllication and remove it from Person
    appl  = add_state(_('application'),                'Application', initial=True)
    prop  = add_state(_('send interview proposition'), 'Application')
    itne  = add_state(_('interview time negociation'), 'Application')
    itpl  = add_state(_('interview planned'),          'Application')
    itju  = add_state(_('interview judgment'),         'Application')
    spoa  = add_state(_('send positive answer'),       'Application')
    snea  = add_state(_('send negative answer'),       'Application')
    refu  = add_state(_('refused'),                    'Application')
    recr  = add_state(_('recruited'),                  'Application')
    canc  = add_state(_('canceled'),                   'Application')
    add_transition(_('cancel application'), 'Application', (appl, prop, itne, itpl, itju, spoa, snea, refu, recr),  canc)
    add_transition(_('discard application'), 'Application', (appl, itju),  snea)
    add_transition(_('negative answer sent'), 'Application', (snea,),  refu)
    add_transition(_('propose interview'), 'Application', (appl,),  prop)
    add_transition(_('schedule interview'), 'Application', (appl,),  itne)
    add_transition(_('interview scheduled'), 'Application', (itne,),  itpl)
    add_transition(_('interview done'), 'Application', (itpl,),  itju)
    add_transition(_('propose new interview'), 'Application', (itju,),  prop)
    add_transition(_('accept application'), 'Application', (itju, ),  spoa)
    add_transition(_('application accepted'), 'Application', (spoa,),  recr)
    checkpoint()

if confirm('insert application for each person?'):

    state_changed ={u'jugement candidature': u'application',
                    u'envoi réponse négative': u'send negative answer',
                    u'envoi proposition entretien': u'send interview proposition',
                    u'négociation horaire entretien': u'interview time negociation',
                    u'jugement entretien': u'interview judgment',
                    u'entretien convenu': u'send interview proposition',
                    u'envoi réponse positive': u'send positive answer',
                    u'refusé': u'refused',
                    u'recruté': u'recruited',
                    u'abandon': u'canceled',
                    u'annulé': u'canceled'}

    ##migrate state form person to application

    for person in rql('Any P,S,SN WHERE P is Person, P in_state S, S name SN').entities():
        assert rql(u'INSERT Application X : X for_person P, X in_state S '
                   'WHERE P eid %(eid)s, S name %(state)s',
                   {'eid': person.eid, 'state': state_changed[person.state]},
                   ask_confirm=False)
    checkpoint()

# delete state for Person
drop_relation_definition('Person', 'in_state', 'State')
drop_relation_definition('Person', 'wf_info_for', 'TrInfo')
drop_attribute('Person', 'address')

rql('DELETE State S WHERE S state_of X, X name "Person"')

