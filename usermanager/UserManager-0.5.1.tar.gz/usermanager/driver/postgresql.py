"""\
A PostgreSQL implementation of the UserManager API
"""

import datetime

# Backwards compatibility with AuthKit
from usermanager.driver.base import *

def _nothing(a):
    return a

def create_tables(service, drop_first=False, name='user'):
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    sql = """
        CREATE TABLE authkit_group (
            uid serial UNIQUE NOT NULL,
            name character varying(255) UNIQUE NOT NULL
        );

        CREATE TABLE authkit_role (
            uid serial UNIQUE NOT NULL,
            name character varying(255) UNIQUE NOT NULL
        );

        CREATE TABLE authkit_user (
            uid serial UNIQUE NOT NULL,
            username character varying(255) UNIQUE NOT NULL,
            password character varying(255) NOT NULL,
            group_uid integer REFERENCES authkit_group (uid)
        );

        CREATE TABLE authkit_user_role (
            uid serial UNIQUE NOT NULL,
            user_uid integer REFERENCES authkit_user (uid),
            role_uid integer REFERENCES authkit_role (uid)
        );

    """
    if drop_first:
        sql += """
            DROP TABLE authkit_group;
            DROP TABLE authkit_role;
            DROP TABLE authkit_user;
            DROP TABLE authkit_user_role;
        """
    cursor.execute(sql)
    cursor.close()

# Create Methods
def user_create(
    service,
    username,
    password,
    group=None,
    name='user',
    encrypt=_nothing,
):
    """\
    Create a new user with the username, password and group name specified.
    """
    if ' ' in username:
        raise UserManagerError("Usernames cannot contain space characters")
    if user_exists(service, username, name=name):
        raise UserManagerError("User %r already exists"%username) 
    if group is not None and not group_exists(service, group, name=name):
        raise NoSuchGroupError(
            "There is no such group %r"%group
        )
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    if group is not None:
        cursor.execute(
            """
            SELECT uid FROM authkit_group WHERE name=%s
            """,
            (group.lower(),)
        )
        group_uid = cursor.fetchall()[0][0]
    else:
        group_uid = None
    cursor.execute(
        """
        INSERT INTO authkit_user (username, password, group_uid) VALUES (%s, %s, %s)
        """,
        (username, encrypt(password), group_uid)
    )
    cursor.close()

def role_create(service, role, name='user'):
    """\
    Add a new role to the system
    """
    if ' ' in role:
        raise UserManagerError("Roles cannot contain space characters")
    if role_exists(service, role, name=name):
        raise UserManagerError("Role %r already exists"%role)
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO authkit_role (name) VALUES (%s)
        """,
        (role.lower(),)
    )
    cursor.close()

def group_create(service, group, name='user'):
    """\
    Add a new group to the system
    """
    if ' ' in group:
        raise UserManagerError("Groups cannot contain space characters")
    if group_exists(service, group, name=name):
        raise UserManagerError("Group %r already exists"%group)
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO authkit_group (name) VALUES (%s)
        """,
        (group.lower(),)
    )
    cursor.close()

# Delete Methods
def user_delete(service, username, name='user'):
    """\
    Remove the user with the specified username
    """
    if not user_exists(service, username.lower(), name=name):
        raise UserManagerError("There is no such user %r"%username)
    else:
        database_name = service[name].connection_name
        conn = service[database_name].connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM authkit_user WHERE username=%s
            """,
            (username.lower(),)
        )
        cursor.close()

def role_delete(service, role, name='user'):
    """\
    Remove the role specified. Rasies an exception if the role is still in use.
    To delete the role and remove it from all existing authkit_user use
    ``role_delete_cascade()``
    """
    if not role_exists(service, role.lower(), name=name):
        raise UserManagerError("There is no such role %r"%role)
    else:
        database_name = service[name].connection_name
        conn = service[database_name].connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT count(name) FROM authkit_user_role
            LEFT OUTER JOIN authkit_role ON authkit_user_role.role_uid = authkit_role.uid
            WHERE authkit_role.name=%s
            """,
            (role.lower(),)
        )
        if cursor.fetchall()[0][0] > 0:
            raise UserManagerError("The role is still being used and therefore cannot be deleted"%(role.lower()))

        cursor.execute(
            """
            DELETE FROM authkit_role WHERE name=%s
            """,
            (role.lower(),)
        )
        cursor.close()

def group_delete(service, group, name='user'):
    """\
    Remove the group specified. Rasies an exception if the group is still in use.
    To delete the group and remove it from all existing authkit_user use ``group_delete_cascade()``
    """
    if not group_exists(service, group.lower(), name=name):
        raise UserManagerError("There is no such group %r"%group)
    else:
        database_name = service[name].connection_name
        conn = service[database_name].connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT count(group_uid) FROM authkit_user
            LEFT OUTER JOIN authkit_group ON authkit_user.group_uid = authkit_group.uid
            WHERE authkit_group.name=%s
            """,
            (group.lower(),)
        )
        if cursor.fetchall()[0][0] > 0:
            raise UserManagerError("The group %r is still being used and therefore cannot be deleted"%(group.lower()))

        cursor.execute(
            """
            DELETE FROM authkit_group WHERE name=%s
            """,
            (group.lower(),)
        )
        cursor.close()

# Existence Methods
def user_exists(service, username, name='user'):
    """\
    Returns ``True`` if a user exists with the given username, ``False``
    otherwise. Usernames are case insensitive.
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT count(username) FROM authkit_user WHERE username=%s
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0] > 0

def role_exists(service, role, name='user'):
    """\
    Returns ``True`` if the role exists, ``False`` otherwise. Roles are
    case insensitive.
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT count(name) FROM authkit_role WHERE name=%s
        """,
        (role.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0] > 0

def group_exists(service, group, name='user'):
    """\
    Returns ``True`` if the group exists, ``False`` otherwise. Groups
    are case insensitive.
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT count(name) FROM authkit_group WHERE name=%s
        """,
        (group.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0] > 0

# List Methods
def list_roles(service, name='user'):
    """\
    Returns a lowercase list of all roll names ordered alphabetically
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name FROM authkit_role ORDER BY name
        """,
    )
    rows = cursor.fetchall()
    cursor.close()
    return [row[0] for row in rows]

def list_users(service, name='user'):
    """\
    Returns a lowecase list of all usernames ordered alphabetically
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT username FROM authkit_user ORDER BY username
        """,
    )
    rows = cursor.fetchall()
    cursor.close()
    return [row[0] for row in rows]

def list_groups(service, name='user'):
    """\
    Returns a lowercase list of all authkit_group ordered alphabetically
    """
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name FROM authkit_group ORDER BY name
        """,
    )
    rows = cursor.fetchall()
    cursor.close()
    return [row[0] for row in rows]

# User Methods
def user(service, username, name='user'):
    """\
    Returns a dictionary in the following format:

    ::

        {
            'username': username,
            'group':    group,
            'password': password,
            'authkit_role':    [role1,role2,role3... etc]
        }

    Role names are ordered alphabetically
    Raises an exception if the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT username, name, password FROM authkit_user
        LEFT OUTER JOIN authkit_group
            ON authkit_user.group_uid=authkit_group.uid
        WHERE authkit_user.username=%s
        ORDER BY username
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()[0]
    cursor.close()

    return {
        'username': rows[0],
        'group':    rows[1],
        'password': rows[2],
        'authkit_role':    user_roles(service, username, name=name)
    }

def user_roles(service, username, name='user'):
    """\
    Returns a list of all the role names for the given username ordered
    alphabetically. Raises an exception if the username doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT authkit_role.name FROM authkit_user_role
        JOIN authkit_user on authkit_user.uid = authkit_user_role.user_uid
        JOIN authkit_role on authkit_user_role.role_uid = authkit_role.uid
        WHERE authkit_user.username=%s
        ORDER BY authkit_role.name
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return [x[0] for x in rows]

def user_group(service, username, name='user'):
    """\
    Returns the group associated with the user or ``None`` if no group is
    associated. Raises an exception is the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT authkit_group.name FROM authkit_group
        LEFT OUTER JOIN authkit_user on authkit_user.group_uid = authkit_group.uid
        WHERE authkit_user.username=%s
        ORDER BY authkit_group.name
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0]

def user_password(service, username, name='user'):
    """\
    Returns the password associated with the user or ``None`` if no
    password exists. Raises an exception is the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT password FROM authkit_user
        WHERE username=%s
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0]

def user_has_role(service, username, role, name='user'):
    """\
    Returns ``True`` if the user has the role specified, ``False``
    otherwise. Raises an exception if the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    if not role_exists(service, role.lower(), name=name):
        raise NoSuchRoleError("No such role %r"%role.lower())
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT count(authkit_user_role.role_uid) FROM authkit_user_role
        LEFT OUTER JOIN authkit_user
            ON authkit_user.uid = authkit_user_role.user_uid
        LEFT OUTER JOIN authkit_role
            ON authkit_user_role.role_uid = authkit_role.uid
        WHERE authkit_role.name=%s and authkit_user.username = %s
        """,
        (role.lower(), username.lower())
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0] > 0

def user_has_group(service, username, group, name='user'):
    """\
    Returns ``True`` if the user has the group specified, ``False``
    otherwise. The value for ``group`` can be ``None`` to test that
    the user doesn't belong to a group. Raises an exception if the
    user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    if group is not None and not \
       group_exists(service, group.lower(), name=name):
        raise NoSuchGroupError("No such group %r"%group.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT authkit_group.name FROM authkit_user
        LEFT OUTER JOIN authkit_group
            ON authkit_user.group_uid = authkit_group.uid
        WHERE authkit_group.name=%s and authkit_user.username = %s
        """,
        (group.lower(), username.lower())
    )
    rows = cursor.fetchall()
    cursor.close()
    if rows:
        group_ = rows[0][0]
    else:
        return False
    if group is None:
        if group_ == None:
            return True
    else:
        if group is not None and group_ == group.lower():
            return True
    return False

def user_has_password(
    service,
    username,
    password,
    name='user',
    encrypt=_nothing,
):
    """\
    Returns ``True`` if the user has the password specified, ``False``
    otherwise. Passwords are case sensitive. Raises an exception if the
    user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT password FROM authkit_user
        WHERE username = %s
        """,
        (username.lower(),)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows[0][0] == encrypt(password)

def user_set_username(service, username, new_username, name='user'):
    """\
    Sets the user's username to the lowercase of new_username.
    Raises an exception if the user doesn't exist or if there is already
    a user with the username specified by ``new_username``.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    if user_exists(service, new_username.lower(), name=name):
        raise UserManagerError(
            "A user with the username %r already exists"%username.lower()
        )

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE authkit_user SET username=%s WHERE username=%s
        """,
        (new_username.lower(), username.lower())
    )
    cursor.close()

def user_set_password(
    service,
    username,
    new_password,
    encrypt=_nothing,
    name='user'
):
    """\
    Sets the user's password. Should be plain text, will be encrypted using
    ``encrypt()``. Raises an exception if the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE authkit_user SET password=%s WHERE username=%s
        """,
        (encrypt(new_password), username.lower())
    )
    cursor.close()

def user_set_group(
    service,
    username,
    group,
    auto_add_group=False,
    name='user',
):
    """\
    Sets the user's group to the lowercase of ``group`` or ``None``. If
    the group doesn't exist and ``add_if_necessary`` is ``True`` the
    group will also be added. Otherwise a ``NoSuchGroupError``
    will be raised. Raises an exception if the user doesn't exist.
    """
    if group is None:
        return user_remove_group(service, username, name=name)
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())
    if not group_exists(service, group.lower(), name=name):
        if auto_add_group:
            group_create(service, group.lower(), name=name)
        else:
            raise NoSuchGroupError("No such group %r"%group.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT uid FROM authkit_group WHERE name=%s
        """,
        (group.lower(),)
    )
    group_uid = cursor.fetchall()[0][0]
    cursor.execute(
        """
        UPDATE authkit_user SET group_uid=%s WHERE username=%s
        """,
        (group_uid, username.lower())
    )
    cursor.close()

def user_add_role(service, username, role, auto_add_role=False, name='user'):
    """\
    Sets the user's role to the lowercase of ``role``. If the role doesn't
    exist and ``add_if_necessary`` is ``True`` the role will also be
    added. Otherwise an ``NoSuchRoleError`` will be raised. Raises
    an exception if the user doesn't exist.
    """
    if user_has_role(service, username, role, name=name):
        return
    if not role_exists(service, role.lower(), name=name):
        if auto_add_role:
            role_create(service, role.lower(), name=name)
        else:
            raise NoSuchRoleError("No such role %r"%role.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT uid FROM authkit_user WHERE username=%s
        """,
        (username.lower(),)
    )
    user_uid = cursor.fetchall()[0][0]

    cursor.execute(
        """
        SELECT uid FROM authkit_role WHERE name=%s
        """,
        (role.lower(),)
    )
    role_uid = cursor.fetchall()[0][0]

    cursor.execute(
        """
        INSERT INTO authkit_user_role (user_uid, role_uid) VALUES (%s, %s);
        """,
        (user_uid, role_uid)
    )
    cursor.close()

def user_remove_role(service, username, role, name='user'):
    """\
    Removes the role from the user specified by ``username``. Raises
    an exception if the user doesn't exist.
    """
    if not user_has_role(service, username, role, name=name):
        raise UserManagerError(
            "No role %r found for user %r"%(role.lower(), username.lower())
        )
    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT uid FROM authkit_user WHERE username=%s
        """,
        (username.lower(),)
    )
    user_uid = cursor.fetchall()[0][0]

    cursor.execute(
        """
        SELECT uid FROM authkit_role WHERE name=%s
        """,
        (role.lower(),)
    )
    role_uid = cursor.fetchall()[0][0]

    cursor.execute(
        """
        DELETE FROM authkit_user_role WHERE user_uid=%s and role_uid=%s;
        """,
        (user_uid, role_uid)
    )
    cursor.close()

def user_remove_group(service, username, name='user'):
    """\
    Sets the group to ``None`` for the user specified by ``username``.
    Raises an exception if the user doesn't exist.
    """
    if not user_exists(service, username.lower(), name=name):
        raise NoSuchUserError("No such user %r"%username.lower())

    database_name = service[name].connection_name
    conn = service[database_name].connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE authkit_user SET group_uid=%s WHERE username=%s
        """,
        (None, username.lower())
    )
    cursor.close()

