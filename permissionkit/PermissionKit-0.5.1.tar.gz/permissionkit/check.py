"""\
Functions to facilitate checking permissions
"""

def check(
    marble, 
    permission, 
    on_pass, 
    on_not_authenticated, 
    on_not_authorized
):
    """\
    Check a permission and automatically handle the result
    """
    result = permission(marble)
    if result == True:
        return on_pass(marble)
    elif result == 'not_authenticated':
        return on_not_authenticated(marble)
    elif result == 'not_authorized':
        return on_not_authorized(marble)
    else:
        raise Exception('Unexpected result %r from permission %r'%(result, permission))

def prepare_check(
    on_pass, 
    on_not_authenticated, 
    on_not_authorized,
):
    def prepared_check(marble, permission):
        return check(
            marble,
            permission, 
            on_not_authenticated=on_not_authenticated, 
            on_not_authorized=on_not_authorized,
        )
    return prepared_check

def prepare_proceed_if(
    on_fail=None, 
    on_not_authenticated=None, 
    on_not_authorized=None
):
    def prepared_proceed_if(permission):
        return proceed_if(
            permission, 
            on_fail=on_fail, 
            on_not_authenticated=on_not_authenticated, 
            on_not_authorized=on_not_authorized,
        )
    return prepared_proceed_if

def proceed_if(
    permission, 
    on_fail=None, 
    on_not_authenticated=None, 
    on_not_authorized=None
):
    """\
    Used like this:

    ::

        @proceed_if(is_valid_user, on_fail=return_401_response)
        @proceed_if(
            is_valid_user, 
            on_not_authenticated=redirect_to_signin,  
            on_not_authorized=return_403_response,
        )

    """
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authenticated()' handler has been specified")
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authorized()' handler has been specified")
    def decorator(func):
        def action(marble):
            return check(
                marble,
                permission, 
                on_not_authenticated=on_not_authenticated,
                on_not_authorized=on_not_authorized,
                on_pass = func,
            )
        action.__doc__ = func.__doc__
        return action
    return decorator

def proceed_if_action(
    permission, 
    on_fail=None, 
    on_not_authenticated=None, 
    on_not_authorized=None
):
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authenticated()' handler has been specified")
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authorized()' handler has been specified")
    def decorator(func):
        def action(self, marble):
            def on_pass(marble):
                return func(self, marble)
            return check(
                marble,
                permission, 
                on_not_authenticated=on_not_authenticated,
                on_not_authorized=on_not_authorized,
                on_pass = on_pass,
            )
        action.__doc__ = func.__doc__
        return action
    return decorator

def proceed_if_api(
    permission, 
    on_fail=None, 
    on_not_authenticated=None, 
    on_not_authorized=None
):
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authenticated()' handler has been specified")
    if on_not_authenticated is None:
        if on_fail is not None:
            on_not_authenticated = on_fail
        else:
            raise Exception("No 'on_not_authorized()' handler has been specified")
    def decorator(func):
        def action(marble, event):
            def on_pass(marble):
                return func(marble, event)
            return check(
                marble,
                permission, 
                on_not_authenticated=on_not_authenticated,
                on_not_authorized=on_not_authorized,
                on_pass = on_pass,
            )
        action.__doc__ = func.__doc__
        return action
    return decorator


