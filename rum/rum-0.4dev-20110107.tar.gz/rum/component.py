from rumcomponent import Component

class Component(Component):
    def config(self):
        from rum import app
        assert app, "Ooops, app should have been there"
        return app.config
    config = property(
        fget=config,
        doc="The configuration mapping where implementators and their arguments"
            " are declared"
        )