"""\
Decorators to ensure the bag has entered the required pipes
"""

from pipestack.app import PipeError

def ensure_method_marble(*pipes, **options):
    def outer(func):
        def inner(self, marble, *k, **p):
            if 'when' in options:
                if not options['when'](marble):
                    return func(self, marble, *k, **p)
            for name in pipes:
                if hasattr(marble, 'aliases') and marble.aliases is not None \
                   and name in marble.aliases:
                    name = marble.aliases[name]
                if not marble.bag.has_key(name):
                    marble.bag.enter(name)
            return func(self, marble, *k, **p)
        return inner
    return outer

def ensure_method_bag(*pipes, **options):
    def outer(func):
        def inner(self, bag, *k, **p):
            if 'when' in options:
                if not options['when'](bad):
                    return func(self, bag, *k, **p)
            for name in pipes:
                if hasattr(self, 'aliases') and self.aliases is not None \
                   and name in self.aliases:
                    name = self.aliases[name]
                if not bag.has_key(name):
                    try:
                        bag.enter(name)
                    except PipeError, e:
                        raise PipeError(
                            'Couldn\'t start pipe %r when calling %r. %s'%(
                                name, 
                                func, 
                                e
                            )
                        )
            return func(self, bag, *k, **p)
        return inner
    return outer

def ensure_function_marble(*pipes, **options):
    def outer(func):
        def inner(marble, *k, **p):
            if 'when' in options:
                if not options['when'](marble):
                    return func(marble, *k, **p)
            for name in pipes:
                if hasattr(marble, 'aliases') and marble.aliases is not None \
                   and name in marble.aliases:
                    name = marble.aliases[name]
                if not marble.bag.has_key(name):
                    marble.bag.enter(name)
            return func(marble, *k, **p)
        return inner
    return outer

def ensure_self_marble(*pipes, **options):
    def outer(func):
        def inner(self, *k, **p):
            if 'when' in options:
                if not options['when'](self):
                    return func(self, *k, **p)
            for name in pipes:
                if hasattr(self, 'aliases') and self.aliases is not None \
                   and name in self.aliases:
                    name = self.aliases[name]
                if not self.bag.has_key(name):
                    self.bag.enter(name)
            return func(self, *k, **p)
        return inner
    return outer

def ensure_function_bag(*pipes, **options):
    def outer(func):
        def inner(bag, *k, **p):
            if 'when' in options:
                if not options['when'](bag):
                    return func(bag, *k, **p)
            for name in pipes:
                if not bag.has_key(name):
                    bag.enter(name)
            return func(bag, *k, **p)
        return inner
    return outer

# Set up useful aliases:
#ensure = ensure_function_bag

# Different "when" functions
def marble_option_is_true(option):
    def marble_option_is_true_check(marble):
        if getattr(marble.config, option, False) is True:
            return True
        return False
    return marble_option_is_true_check

def bag_option_is_true(name, option):
    def bag_option_is_true_check(bag):
        if getattr(bag.config[name], option, False) is True:
            return True
        return False
    return bag_option_is_true_check

