from bn import AttributeDict

def userService():
    def userService_constructor(service):
        name = service.name
        service.app.config[name] = AttributeDict(service.app.option[name].copy())
        def start(service):
            def user_has_password(username, password):
                if username == service.app.config[name].username and \
                   password == service.app.config[name].password:
                    return True
                return False
            service[name] = AttributeDict(user_has_password=user_has_password)
        return AttributeDict(start=start)
    return userService_constructor
