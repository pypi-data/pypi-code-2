# application are taggable
add_relation_definition('Tag','tags','Application')
# move tags from person to applications
rql('SET T tags A WHERE T tags P, P is Person, A for_person P')
rql('DELETE T tags P WHERE P is Person')
checkpoint()

# fix wflow
pending = add_state(u'recruitment pending','Application')
pos = rql('Any S WHERE S name "send positive answer"')[0][0]
add_transition(u'sent positive answer', 'Application', (pos,), pending)

rql('SET S name "received" WHERE S is State, S name "application"', ask_confirm=False)
rql('SET S name "rejected" WHERE S is State, S name "refused"', ask_confirm=False)
rql('SET S name "interview scheduling" WHERE S is State, S name "interview time negociation"', ask_confirm=False)
rql('SET S name "notify accept" WHERE S is State, S name "send positive answer"', ask_confirm=False)
rql('SET S name "notify reject" WHERE S is State, S name "send negative answer"', ask_confirm=False)
rql('SET S name "decision pending" WHERE S is State, S name "interview judgment"', ask_confirm=False)

rql('SET T name "reject application" WHERE T is Transition, T name "discard application"', ask_confirm=False)
rql('SET T name "recruitment accepted" WHERE T is Transition, T name "application accepted"', ask_confirm=False)
rql('SET T name "accept interview" WHERE T is Transition, T name "interview scheduled"', ask_confirm=False)
rql('SET T name "send negative answer" WHERE T is Transition, T name "negative answer sent"', ask_confirm=False)
rql('SET T name "send positive answer" WHERE T is Transition, T name "sent positive answer"', ask_confirm=False)

rql('SET A in_state S WHERE S name "interview scheduling", A in_state X, X name "send interview proposition"', ask_confirm=False)

rql('DELETE Transition T WHERE T name "propose interview"', ask_confirm=False)
rql('DELETE Transition T WHERE T name "propose new interview"', ask_confirm=False)
rql('DELETE State S WHERE S name "send interview proposition"', ask_confirm=False)

rql('SET S allowed_transition T WHERE S name "recruitment pending", T name "cancel application"', ask_confirm=False)
rql('SET S allowed_transition T WHERE S name "recruitment pending", T name "recruitment accepted"', ask_confirm=False)
rql('SET S allowed_transition T WHERE S name "decision pending", T name "schedule interview"', ask_confirm=False)

rql('DELETE S allowed_transition T WHERE S name "recruited", T name "cancel application"', ask_confirm=False)
rql('DELETE S allowed_transition T WHERE S name "rejected", T name "cancel application"', ask_confirm=False)
rql('DELETE S allowed_transition T WHERE S name "notify accept", T name "recruitment accepted"', ask_confirm=False)
checkpoint()
