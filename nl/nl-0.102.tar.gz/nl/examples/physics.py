
class Monad(Thing): pass

class Diad(Thing): pass

class Is(Exists):
    subject = Monad
    mods = {'in': Diad}

class Form(Thing): pass


class Relates(Exists):
    subject = Form
    mods = {'what': Diad,
            'distance': Number}


class Lives(Exists):
    subject = Monad
    mods = {'the_form': Form}




Rule([
    Fact(Monad('M1'), Interacts(with=Monad('M2')), Instant('I1')),
],[
    Fact(Monad('M2'), Interacts(with=Monad('M1')), Instant('I1')),
])
