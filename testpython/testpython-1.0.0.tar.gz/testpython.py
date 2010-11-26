class A(object):
    def routine(self):
        print "A's routine"


class B(A):
    def routine(self):
        print "B's routine"
        super(B,self).routine()


b=B()
b.routine()
