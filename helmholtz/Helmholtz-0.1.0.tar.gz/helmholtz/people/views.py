#encoding:utf-8
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.schema import cast_queryset
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page
from helmholtz.access_control.filters import get_downloadable_by
from helmholtz.access_control.proxies import ProxyUser
from helmholtz.people.models import Contact, ScientificStructure, Position
from helmholtz.people.forms import CreatePositionForm, ContactForm, EMailForm, WebSiteForm, AddressForm, FaxForm, PhoneForm
from helmholtz.trackers.models import EMailTracker, UserEMailTracker, GroupEMailTracker
from helmholtz.storage.models import File

@login_required
@memorise_last_page
@memorise_last_rendered_page
def lab_list(request, template):
    """Get all laboratories and teams registered in the database and organise them in a hierarchical manner.
    
    NB :
    
    As template engine cannot render a hierarchical structure,
    laboratories and teams must be organised on two levels :
    
    - the first level occupied by laboratories with parent = None
    - the second level occupied by teams with parent = laboratory
    
    """
    laboratories = ScientificStructure.objects.filter(parent__pk__isnull=True)
    context = {'labs':laboratories, 'user':request.user, 'current_page':request.session['last_page']}
    response = render_to_response(template, context)
    return response

def get_form_context(request, form, header, action=None, next_step=None):
    context = {'form':form,
               'form_header':header,
               'cancel_redirect_to':request.session['last_page'],
               'enable_scroll_position':True,
               'action':action,
               'background_page':request.session['background_page'],
               'next_step':next_step}
    return context

def contact(request, receiver_id=None, group_id=None, **kwargs):
    """Display or process the contact form useful for users 
    to ask information about catdb or helmholtz."""
    #current_page,url = resolve_current_page(request)
    #user_id = url[2].get('user_id',None)
    #user = User.objects.get(pk=int(user_id)) if user_id else request.user
    #template = url[2]['template']
    if receiver_id :
        recipient = User.objects.get(pk=int(receiver_id))
        emails = [recipient.email]
        header = 'Contact %s' % (recipient.get_full_name())
        subclass = UserEMailTracker
    else :
        if group_id :
            recipient = Group.objects.get(pk=int(group_id))
            if recipient.name == 'admin' :
                header = 'Contact the database administrators'
            else :
                header = 'Contact all member of group %s' % (recipient.name)
        else :
            recipient = Group.objects.get(name='admin')
            header = 'Contact the database administrators'
        subclass = GroupEMailTracker
        recipients = User.objects.filter(groups__pk=recipient.pk)
        emails = [k.email for k in recipients]
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # ought to give some sort of feedback, and maybe return to wherever the user was before clicking 'contact'
            cform = form.cleaned_data
            username = "anonymous user" if request.user.is_anonymous() else request.user.username
            subject = "[%s]-[%s] %s" % (settings.PROJECT_NAME, username, cform['subject'])
            send_mail(subject, cform['message'], cform['sender'], emails, fail_silently=False)
            #store message in database
            subclass.objects.create(sender=request.user,
                                    recipient=recipient,
                                    subject=cform['subject'],
                                    message=cform['message'])
            return HttpResponseRedirect('.')#current_page)
    else:
        if hasattr(request.user, "email"):
            form = ContactForm(initial={'sender':request.user.email})
        else:
            form = ContactForm()
    context = get_form_context(request, form, header)
    context.update(kwargs)
    return render_to_response(kwargs['template'], context)

def common_contact(request, form_type, user, subclass, contact=None, **kwargs):
    if request.method == 'POST':
        if not contact :
            form = form_type(request.POST)
        else :
            form = form_type(request.POST, instance=contact)
        if form.is_valid() :
            instance = form.save()
            if not contact :
                user.profile.contacts.add(instance)
            return HttpResponseRedirect(reverse('user-profile', args=[user.pk]))
        else :
            form_header = 'Create a new %s' % subclass
    else:
        if not contact :
            form = form_type()
        else :
            form = form_type(instance=contact)
        form_header = 'Create a new %s' % subclass
    context = get_form_context(request, form, form_header)
    context.update(kwargs)
    return render_to_response(kwargs['template'], context)
 
@login_required
def create_contact(request, subclass, user_id, **kwargs):
    """display or process the contact form."""
    user = User.objects.get(pk=int(user_id))
    form_map = {'email':EMailForm,
                'phone':PhoneForm,
                'fax':FaxForm,
                'website':WebSiteForm,
                'address':AddressForm}
    form_type = form_map[subclass]
    return common_contact(request, form_type, user, subclass, **kwargs)

@login_required
def update_contact(request, user_id, contact_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    contact = cast_object_to_leaf_class(Contact.objects.get(pk=int(contact_id)))
    subclass = contact.__class__.__name__.lower()
    form_map = {'email':EMailForm,
                'phone':PhoneForm,
                'fax':FaxForm,
                'website':WebSiteForm,
                'address':AddressForm}
    form_type = form_map[subclass]
    return common_contact(request, form_type, user, subclass, contact, **kwargs)

@login_required
def delete_contact(request, user_id, contact_id):
    user = User.objects.get(pk=int(user_id))
    contact = user.profile.contacts.get(pk=int(contact_id))
    contact.delete()
    redirection = reverse('user-profile', args=[user.pk])
    return HttpResponseRedirect(redirection)

def subtract_months(dt, m):
    years = m / 12
    months = m - 12 * years
    if dt.month <= months :
        years += 1
    year = dt.year - years
    month = (dt.month - months - 1) % 12 + 1
    return datetime(year, month, 1)#here day is fixed because just year and month is interesting

def get_user_context(request, user):
    dct = dict()
    request_user = request.user
    
    try :
        profile = user.profile
    except :
        profile = None
    #adding contact data
    if profile :
        queryset = profile.contacts.all()
        #emails = cast_queryset(queryset,"EMail")
        phones = cast_queryset(queryset, "Phone")
        faxes = cast_queryset(queryset, "Fax")
        websites = cast_queryset(queryset, "WebSite")
        addresses = cast_queryset(queryset, "Address")
    else :
        #emails = None
        phones = None
        faxes = None
        websites = None
        addresses = None
    contacts = [#{'key':'E-mails','objects':emails,'subclass':'email'},
                {'key':'Phones', 'objects':phones, 'subclass':'phone'},
                {'key':'Faxes', 'objects':faxes, 'subclass':'fax'},
                {'key':'Websites', 'objects':websites, 'subclass':'website'},
                {'key':'Addresses', 'objects':addresses, 'subclass':'address'},
    ]
    #sent and received mails
    #received
    pks = [k.pk for k in user.mails_as_recipient.all()]
    from_groups = list()
    for group in user.groups.all() :
        from_groups.extend([k.pk for k in group.mails_as_recipient.all()])
    pks.extend(from_groups)
    received_emails = EMailTracker.objects.filter(pk__in=pks)
    #sent
    sent_emails = user.mails_as_sender.all()
    user_sent_emails = cast_queryset(sent_emails, 'UserEMailTracker')
    group_sent_emails = cast_queryset(sent_emails, 'GroupEMailTracker')
    sent_by_server_emails = user_sent_emails.count() + sum([k.recipient.user_set.count() for k in group_sent_emails])
    
    #adding access request
    #requested_files = cast_queryset(user.requests.all(),'file')
    #requests = {''}
    #compute connections histogram
    #by months
    by_months = list()
    c_objects = user.connectiontracker_set.all().order_by('-date')
    today = datetime.now()
    month_range = 6
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    last_date = today
    for m in range(0, month_range + 1) :
        new_date = subtract_months(today, m)
        if new_date < datetime(user.date_joined.year, user.date_joined.month, 1) : 
            break
        c_filtered = c_objects.filter(date__gte=new_date).filter(date__lt=last_date)
        data = {'quantity':c_filtered.count(), 'label':"%s %s" % (month_map[new_date.month], str(new_date.year)[2:])}
        by_months.append(data)
        last_date = new_date
    by_months.reverse()
    
    #by weeks
    dct['connections'] = dict() 
    dct['connections']['by_months'] = by_months
    dct['received_emails'] = received_emails
    dct['user_sent_emails'] = user_sent_emails
    dct['group_sent_emails'] = group_sent_emails
    dct['sent_by_server_emails'] = sent_by_server_emails
    dct['now'] = datetime.now()
    dct['user'] = user
    dct['proxy_user'] = ProxyUser.objects.get(pk=user.pk)
    dct['request_user'] = request_user
    dct['profile'] = profile
    dct['contacts'] = contacts 
    dct['downloadables'] = get_downloadable_by(File.objects.all(), user)
    dct['members'] = User.objects.filter(groups__pk__in=[k.pk for k in user.groups.all()]).exclude(pk=user.pk).order_by('last_name').distinct()
    return dct

@login_required
@memorise_last_page
@memorise_last_rendered_page
def show_profile(request, user_id, template):
    user = User.objects.get(pk=int(user_id))
    context = get_user_context(request, user)
    #context['current_page'] = request.get_full_path()
    context['enable_scroll_position'] = True
    
    return render_to_response(template, context)
#    if request.user.username == username:
#        user = get_object_or_404(User,username=username)
#        #files = DownloadStack.objects.filter(user=user)
##        have_access = files.filter(state="accepted")
##        access_requested = files.filter(state="requested")
##        access_denied = files.filter(state="rejected")
#        return render_to_response("user_profile.html",
#                                  {'user': user,
##                                   'files': {'have_access': have_access,
##                                             'access_requested': access_requested,
##                                             'access_denied': access_denied},
#                                   })
#    else:
#        return render_to_response("permission_denied.html",
#                                  context_instance=RequestContext(request))

def render_position_context(request, user, form, action=None, next_step=None, **kwargs):
    context = {'action':action,
               'enable_scroll_position':True,
               'form':form,
               'cancel_redirect_to':reverse('user-profile', args=[user.pk]),
               'next_step':next_step}
    context.update(kwargs)
    context.update(get_user_context(request, user))
    return render_to_response("position.html", context)

@login_required
def create_position(request, user_id, *args, **kwargs):
    """display or process the first form of position creation."""
    user = User.objects.get(pk=int(user_id))
    profile = user.profile
    if request.method == 'POST':
        qdct = request.POST.copy()
        qdct['researcher'] = u"%s" % getattr(profile, 'pk', u'')
        form = CreatePositionForm(qdct)
        if form.is_valid() :
            form.save()
            return HttpResponseRedirect(reverse('user-profile', args=[user.pk]))
    else:
        form = CreatePositionForm()
    return render_position_context(request, user, form, **kwargs)

@login_required
def update_position(request, user_id, position_id, *args, **kwargs):
    """display or process the form updating a position."""
    position = Position.objects.get(pk=int(position_id))
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST':
        form = CreatePositionForm(request.POST, instance=position)
        if form.is_valid() :
            form.save()  
            return HttpResponseRedirect(reverse('user-profile', args=[user.pk]))     
    else :
        form = CreatePositionForm(instance=position)
    return render_position_context(request, user, form, **kwargs)

@login_required
def delete_position(request, user_id, position_id):
    user = User.objects.get(pk=int(user_id))
    position = Position.objects.get(pk=position_id)
    position.delete()
    redirection = reverse('user-profile', args=[user.pk])
    return HttpResponseRedirect(redirection)
