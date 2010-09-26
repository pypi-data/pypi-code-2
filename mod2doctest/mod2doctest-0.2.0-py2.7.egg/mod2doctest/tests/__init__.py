# PYTHON
import doctest
# MOD2DOCTEST
import mod2doctest

def run_all():
    for file in ['basicexample.py', 'fulltest.py', 'm2dprint.py']:
        doctest.testfile(file, optionflags=mod2doctest.DEFAULT_DOCTEST_FLAGS)
        

if __name__ == '__main__':
    run_all()

