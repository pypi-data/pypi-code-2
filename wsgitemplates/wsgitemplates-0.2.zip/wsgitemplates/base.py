import os

from paste.script import templates

class BaseTemplate(templates.Template):
    """A basetemplate for creating WSGI applications"""
    
    use_cheetah = True
    
    def run(self, command, output_dir, vars):
        original_output_dir = output_dir
        output_dir = os.path.join(*([vars['egg'], 'src'] + vars['segs']))
        self.pre(command, output_dir, vars)
        self.write_files(command, output_dir, vars)
        self.post(command, original_output_dir, vars)

    def check_vars(self, vars, _):
        vars['type'] = self.entrypoint_type
        vars = templates.Template.check_vars(self, vars, _)
        return vars

    def post(self, command, output_dir, vars):
        setuppy = open(os.path.join(output_dir, "setup.py"), "r")
        s = setuppy.read()
        setuppy.close()

        s = s.replace("# -*- Entry points: -*-", self.getEntrypoints(vars))

        setuppy = open(os.path.join(output_dir, "setup.py"), "w")
        s = setuppy.write(s)
        setuppy.close()

        templates.Template.post(self, command, output_dir, vars)

    def getEntrypoints(self, vars):
        entrypoints = "# -*- Entry points: -*-\n"
        entrypoints += "[%s]\n%s = %s.%s:%s" % (self.entrypoint_type,
                                     vars['entrypointname'],
                                     vars['egg'],
                                     vars['entrypointname'],
                                     vars['entrypointname'].title()+'Factory')
        return entrypoints
