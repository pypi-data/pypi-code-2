def create_quick_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.quick')
    step1 = recipe.add_step(u'action', u'apycot.init', initial=True)
    step2 = recipe.add_step(u'action', u'apycot.get_dependancies')
    recipe.add_transition(step1, step2)
    step3 = recipe.add_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    recipe.add_transition(step2, step3)
    step4 = recipe.add_step(u'action', u'apycot.install', for_each=u'projectenv')
    recipe.add_transition(step3, step4)
    step5 = recipe.add_step(u'action', u'apycot.pyunit', final=True)
    recipe.add_transition(step4, step5)

def create_full_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.full')
    step1 = recipe.add_step(u'action', u'apycot.init', initial=True)
    step2 = recipe.add_step(u'action', u'apycot.get_dependancies')
    step3 = recipe.add_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    step4 = recipe.add_step(u'action', u'apycot.install', for_each=u'projectenv')
    step5bis = recipe.add_step(u'action', u'apycot.python.pylint')
    step5 = recipe.add_step(u'action', u'apycot.pyunit',
                            arguments=u'Options({"pycoverage":True})')
    step6 = recipe.add_step(u'action', u'apycot.pycoverage')
    step7 = recipe.add_step(u'action', u'basic.noop', final=True)
    recipe.add_transition(step1, step2)
    recipe.add_transition(step2, step3)
    recipe.add_transition(step3, step4)
    recipe.add_transition(step4, (step5, step5bis))
    recipe.add_transition(step5, step6)
    recipe.add_transition((step5bis, step6), step7)
    return recipe

# def create_debian_recipe(session):
#     recipe = session.create_entity('Recipe', name=u'apycot.recipe.debian')
#     step1 = recipe.add_step(u'action', u'apycot.init', initial=True)
#     step2 = recipe.add_step(u'action', u'apycot.checkout')
#     step3 = recipe.add_step(u'action', u'apycot.package.lgp_check')
#     step3bis = recipe.add_step(u'action', u'apycot.debian.lgp_build')
#     step4 = recipe.add_step(u'action', u'apycot.debian.lintian')
#     step5 = recipe.add_step(u'action', u'basic.noop', final=True)
#     recipe.add_transition(step1, step2)
#     recipe.add_transition(step2, (step3, step3bis))
#     recipe.add_transition(step3bis, step4)
#     recipe.add_transition((step3, step4), step5)
#     return recipe

# def create_experimental_recipe(session):
#     recipe = session.create_entity('Recipe', name=u'apycot.recipe.experimental')
#     step1 = recipe.add_step(u'recipe', u'apycot.recipe.debian', initial=True)
#     step2 = recipe.add_step(u'action', u'apycot.debian.upload')
#     step3 = recipe.add_step(u'action', u'apycot.debian.publish', final=True)
#     recipe.add_transition(step1, step2)
#     recipe.add_transition(step2, step3)
#     return recipe

# def create_publish_recipe(session):
#     # XXX
#     # copy/upload from logilab-experimental to logilab-public
#     # example: ldi upload logilab-public /path/to/experimental/repo/dists/*/*.changes
#     recipe = session.create_entity('Recipe', name=u'apycot.recipe.publish')
#     return recipe
