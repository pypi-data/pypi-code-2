def noop(context):
    pass

def reinstall(context):
    context.runAllImportStepsFromProfile('profile-plonetheme.responsivetheme:uninstall')
    context.runAllImportStepsFromProfile('profile-plonetheme.responsivetheme:default')
