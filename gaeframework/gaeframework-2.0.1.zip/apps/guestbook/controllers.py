'''
Test application.
'''
from models import Message
from forms import MessageForm

def items_list(app, on_page=10, page=1, template=None):
    greetings = Message.all().order('-date').fetch(on_page)
    return app.render(template or 'guestbook/items_list', {'greetings': greetings})

def create_item(app):
    if app.request.POST:
        # filled form
        form = MessageForm(data=app.request.POST)
        if form.is_valid():
            form.save()
            app.redirect(app.back_url())
    else:
        # empty form
        form = MessageForm()
    # show form with specified data
    return app.render('guestbook/create_item', {'form': form})
