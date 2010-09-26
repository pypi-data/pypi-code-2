# PYTHON
import doctest
# MOD2DOCTEST
import mod2doctest
# TEST
import basicexample_test as A

for mod in [A]:
    doctest.testmod(m=mod, optionflags=mod2doctest.DEFAULT_DOCTEST_FLAGS)


