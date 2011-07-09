'''
User account management.
'''
from apps.user.forms import UserLoginForm, UserRegistrationForm
from apps.user.models import User
from apps.user import login_required


def users_list(app):
    return app.render('user/users_list', {'users': User.all().order("-created")})


def login(app):
    if app.request.POST:
        # filled form
        form = UserLoginForm(data=app.request.POST)
        if form.is_valid():
            nick = form.cleaned_data.get("nick")
            password = form.cleaned_data.get("password")
            user = User.get_by_key_name(nick)
            # correct user
            if user and user.password == password:
                app.session["user"] = user
                # when the user login, that we rotate the session ID (security)
                app.session.regenerate_id()
                return app.redirect("go back")
            else:
                form._errors["nick"] = form.error_class(["User with given nick name and password not found"])
    else:
        # empty form
        form = UserLoginForm()
    return app.render('user/login', {'form': form})

@login_required()
def logout(app):
    del app.session["user"]
    return app.redirect("go back")

def registration(app):
    if app.request.POST:
        # filled form
        form = UserRegistrationForm(data=app.request.POST)
        if form.is_valid():
            # check user nick name duplicates
            nick = form.cleaned_data.get("nick")
            if User.get_by_key_name(nick):
                form._errors["nick"] = form.error_class(["User with given nick name already registered"])
            else:
                user = form.save()
                app.session["user"] = user
                # when the user login, that we rotate the session ID (security)
                app.session.regenerate_id()
                return app.redirect("go back")
    else:
        # empty form
        form = UserRegistrationForm()
    return app.render('user/registration', {'form': form})

def activate(app, account_id):
    '''Activate already registered user account'''
    pass

def deactivate(app, account_id):
    '''Deactivate user account'''
    pass
