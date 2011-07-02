'''
Todo - list of actual tasks.
'''
from google.appengine.api import mail
from apps.user import login_required
from apps.todo.models import Todo
from apps.todo.forms import TodoForm

def todo_list(app, on_page=10, page=1, finished=False):
    todos = Todo.gql("WHERE author = :1 and finished = :2",
                     app.user, finished)
    return app.render('todo/todo_list', {
                      'todos': todos,
                      'todos_pages' : todos.count(),
                      })

def todo_details(app):
    pass

@login_required()
def create_task(app):
    if app.request.POST:
        # filled form
        form = TodoForm(data=app.request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = app.user
            task.save()
            return app.redirect("go back")
    else:
        # empty form
        form = TodoForm()
    # render page
    return app.render('todo/create_task', {'form': form})

@login_required()
def edit_todo(app):
    app.error(404)

@login_required()
def delete_todo(app, todo_id):
    todo_id = int(todo_id)
    todo = Todo.get_by_id(todo_id)
    todo.delete()
    return app.redirect("go back")

@login_required()
def send_mail(app, todo_id):
    todo_id = int(todo_id)
    todo = Todo.get_by_id(todo_id)
    message = mail.EmailMessage(sender  = app.user.email,
                                subject = todo.shortDescription)
    message.to = app.user.email
    message.body = todo.longDescription
    message.send()
    app.redirect('go back')