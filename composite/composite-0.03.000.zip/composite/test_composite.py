from composite import Composite

# test stuff
class PBundle1():
    __required_parts__ = ('__dict__','whosat')
    def repeat(yo, text, count):
        return "%s " % text * count
class PBundle2():
    __magic_parts__ = ('__contains__', )
    def __contains__(yo, name):
        return True
    def repeat(yo):
        pass
    def whosat(yo):
        return "What was that noise?!?  Who's there?  Who's'at?!?"
class BaseClass():
    def repeat(yo, text, count):
        return "----%s----" % text * count
class DerivedClass(BaseClass, metaclass=Composite, parts=(PBundle1, PBundle2)):
    __base_parts__ = ('repeat', )
    #- def repeat(yo, text, count):
    #-     print('whatever...')
    def whatsit(yo, arg1):
        print("calling baseclass's whatsit...")
        print(super().whatsit(arg1))
