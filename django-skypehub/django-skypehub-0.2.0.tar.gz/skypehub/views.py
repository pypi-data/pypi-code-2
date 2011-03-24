from django.http import HttpResponse

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from skypehub.decorators import skype_required
from skypehub.forms import PostMessageForm, PostUserMessageForm

def make_json_response(content):
    return HttpResponse(json.dumps(content, indent=2), content_type='application/javascript')

@skype_required
def list_chats(request, skype):
    chats = []
    for chat in skype.Chats:
        chats.append({
            'name': chat.Name,
            'topic': chat.Topic,
        })
    return make_json_response({'chats': chats})

@skype_required
def post_message(request, skype):
    form = PostMessageForm(request.POST or None)
    if form.is_valid():
        chat = skype.Chat(form.cleaned_data['chat'])
        chat.SendMessage(form.cleaned_data['message'])
        return make_json_response({'result': 'ok'})
    else:
        form = PostUserMessageForm(request.POST or None)
        if form.is_valid():
            chat = skype.CreateChatWith(form.cleaned_data['username'])
            chat.SendMessage(form.cleaned_data['message'])
            return make_json_response({'result': 'ok'})

    return  make_json_response({'result': 'validation error.'})
