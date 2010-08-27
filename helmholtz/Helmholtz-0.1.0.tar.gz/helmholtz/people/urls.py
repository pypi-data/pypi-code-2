from django.conf.urls.defaults import patterns, url, include
from helmholtz.people.admin import community_admin

urlpatterns = patterns('',
    (r'^admin/', include(community_admin.urls)),
    url(r'^lab_list/$', 'helmholtz.people.views.lab_list', {'template':"lab_list.html"}, name='lab-list'),
    url(r'^profile/(?P<user_id>\w*)/$', 'helmholtz.people.views.show_profile', {'template':"user_profile.html"}, name='user-profile'),
    #create
    url(r'^profile/create_position/(?P<user_id>\w*)/$', 'helmholtz.people.views.create_position', {'form_template':"position_form.html", "form_header":"Create a new position"}, name='create-position'),
    #update
    url(r'^profile/update_position/(?P<user_id>\w*)/(?P<position_id>\d+)/$', 'helmholtz.people.views.update_position', {'form_template':"position_form.html", "form_header":"Update an existing position"}, name='update-position'),
    url(r'^profile/delete_position/(?P<user_id>\w*)/(?P<position_id>\d+)/$', 'helmholtz.people.views.delete_position', name='delete-position'),
    #contacts
    url(r'^contact/$', 'helmholtz.people.views.contact', {'template':"contact.html", 'form_template':"contact_form.html"}, name='contact'),
    url(r'^contact_user/(?P<receiver_id>\w*)/$', 'helmholtz.people.views.contact', {'template':"contact.html", 'form_template':"contact_form.html"}, name='contact-user'),
    url(r'^contact_group/(?P<group_id>\w*)/$', 'helmholtz.people.views.contact', {'template':"contact.html", 'form_template':"contact_form.html"}, name='contact-group'),
    url(r'^contact/create/(?P<subclass>\w*)/(?P<user_id>\w*)/$', 'helmholtz.people.views.create_contact', {'template':"user_contact.html", 'form_template':"user_contact_form.html"}, name='create-contact'),
    url(r'^contact/update/(?P<user_id>\w*)/(?P<contact_id>\w*)/$', 'helmholtz.people.views.update_contact', {'template':"user_contact.html", 'form_template':"user_contact_form.html"}, name='update-contact'),
    url(r'^contact/delete/(?P<user_id>\w*)/(?P<contact_id>\w*)/$', 'helmholtz.people.views.delete_contact', name='delete-contact'),
) 
