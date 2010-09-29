import zc.buildout.testing


def recipeSetUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("z3c.coverage", test)
    zc.buildout.testing.install_develop("createzopecoverage", test)


def recipeTearDown(test):
    zc.buildout.testing.buildoutTearDown(test)
