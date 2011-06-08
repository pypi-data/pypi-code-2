def call(app, var, env, ajaxForm=False):
    a = []
    a.append('jqutils/jqutils.js')
    if ajaxForm:
        a.append('jqutils/jquery.form.js')
    return {'toplinks':a}
