"""
:synopsis: remaining "secondary" views for askbot

This module contains a collection of views displaying all sorts of secondary and mostly static content.
"""
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from askbot.forms import FeedbackForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from askbot.utils.forms import get_next_url
from askbot.models import Badge, Award
import askbot

def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))

def faq(request):
    data = {
        'view_name':'faq',
        'gravatar_faq_url': reverse('faq') + '#gravatar',
        #'send_email_key_url': reverse('send_email_key'),
        'ask_question_url': reverse('ask'),
    }
    return render_to_response('faq.html', data, context_instance=RequestContext(request))

def feedback(request):
    data = {'view_name':'feedback'}
    form = None
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                data['email'] = form.cleaned_data.get('email',None)
            data['message'] = form.cleaned_data['message']
            data['name'] = form.cleaned_data.get('name',None)
            message = render_to_response('feedback_email.txt',data,context_instance=RequestContext(request))
            askbot.mail_moderators(_('Q&A forum feedback'), message)
            msg = _('Thanks for the feedback!')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect(get_next_url(request))
    else:
        form = FeedbackForm(initial={'next':get_next_url(request)})

    data['form'] = form
    return render_to_response('feedback.html', data, context_instance=RequestContext(request))
feedback.CANCEL_MESSAGE=_('We look forward to hearing your feedback! Please, give it next time :)')

def privacy(request):
    return render_to_response('privacy.html', {'view_name':'privacy'}, context_instance=RequestContext(request))

def logout(request):#refactor/change behavior?
#currently you click logout and you get
#to this view which actually asks you again - do you really want to log out?
#I guess rationale was to tell the user that s/he may be still logged in
#through their external login sytem and we'd want to remind them about it
#however it might be a little annoying
#why not just show a message: you are logged out of forum, but
#if you really want to log out -> go to your openid provider
    return render_to_response('logout.html', {
        'view_name':'logout',
        'next' : get_next_url(request),
    }, context_instance=RequestContext(request))

def badges(request):#user status/reputation system
    badges = Badge.objects.all().order_by('name')
    my_badges = []
    if request.user.is_authenticated():
        my_badges = Award.objects.filter(user=request.user).values('badge_id')
        #my_badges.query.group_by = ['badge_id']

    return render_to_response('badges.html', {
        'badges' : badges,
        'view_name': 'badges',
        'mybadges' : my_badges,
        'feedback_faq_url' : reverse('feedback'),
    }, context_instance=RequestContext(request))

def badge(request, id):
    badge = get_object_or_404(Badge, id=id)
    awards = Award.objects.extra(
        select={'id': 'auth_user.id', 
                'name': 'auth_user.username', 
                'rep':'auth_user.reputation', 
                'gold': 'auth_user.gold', 
                'silver': 'auth_user.silver', 
                'bronze': 'auth_user.bronze'},
        tables=['award', 'auth_user'],
        where=['badge_id=%s AND user_id=auth_user.id'],
        params=[id]
    ).distinct('id')

    return render_to_response('badge.html', {
        'view_name': badge,
        'awards' : awards,
        'badge' : badge,
    }, context_instance=RequestContext(request))

