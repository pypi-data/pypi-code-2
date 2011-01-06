from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.core.context_processors import csrf
from indeed_contactForm.models import Message
from indeed_contactForm.forms import ContactForm
from django.conf import settings
import datetime



def contact(request,  template, context={}): 
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            m = Message(date=datetime.date.today(), subject=cd['subject'], mail=mail(cd['mail']), message=cd['message'], new=True)
            m.save()
            send_mail(
                cd['subject'],
                cd['message'],
                mail(cd['mail']),
                settings.EMAIL_CONTACT)
            return HttpResponseRedirect('/contact')
    else:
        form = ContactForm()

    c = {'form': form}
    c.update(csrf(request))
    c.update(context)
    return render_to_response(template, c)

def mail(m):
	if m==u"":
		return u"not@entered.de"
	else:
		return m
