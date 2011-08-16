from flask import Flask, request, g, url_for
from flaskext.auth import Auth, AuthUser, logout, Permission, Role, \
        permission_required

app = Flask(__name__)
auth = Auth(app, login_url_name='index')

user_create = Permission('user', 'create')
user_view = Permission('user', 'view')

roles = {
    'admin': Role('admin', [user_create, user_view]),
    'userview': Role('userview', [user_view]),
}

def load_role(role_name):
    return roles.get(role_name)

auth.load_role = load_role

@app.before_request
def init_users():
    """
    Initializing users by hardcoding password. Another use case is to read
    usernames from an external file (like /etc/passwd).
    """
    user = AuthUser(username='user')
    # Setting and encrypting the hardcoded password.
    user.set_and_encrypt_password('password', salt='123')
    # Setting role of the user.
    user.role = 'userview'
    # Persisting users for this request.
    g.users = {'user': user}

@permission_required(resource='user', action='view')
def user_view():
    return 'Users are: {0}.'.format(g.users)

@permission_required(resource='user', action='create')
def user_create():
    return 'I can create users!'

def index():
    if request.method == 'POST':
        username = request.form['username']
        if username in g.users:
            # Authenticate and log in!
            if g.users[username].authenticate(request.form['password']):
                return '''
                        <a href="{0}">View users</a><br/>
                        <a href="{1}">Create users</a>
                        '''.format(url_for('user_view'), url_for('user_create'))
        return 'Failure :('
    return '''
            <form method="POST">
                Username: <input type="text" name="username"/><br/>
                Password: <input type="password" name="password"/><br/>
                <input type="submit" value="Log in"/>
            </form>
            '''

def logout_view():
    user = logout()
    if user is None:
        return 'No user to log out.'
    return 'Logged out user {0}.'.format(user.username)

# URLs
app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
app.add_url_rule('/user/view/', 'user_view', user_view)
app.add_url_rule('/user/create/', 'user_create', user_create)
app.add_url_rule('/logout/', 'logout', logout_view)

# Secret key needed to use sessions.
app.secret_key = 'N4BUdSXUzHxNoO8g'

if __name__ == '__main__':
    app.run(debug=True)
