import os.path
import getopt
import re
from dreamweavertemplate import DreamweaverTemplateInstance, log
from commandtool import Cmd

class DwtToJinja2(Cmd):

    arg_spec=[
        ('DWT_TEMPLATE_DIR', 'The directory containing all the Dreamweaver templates'),
        ('JINJA2_BASE_TEMPLATE_DIR', 'The directory where the Jinja2 base templates should be output'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
    )
    help = {
        'summary': 'convert a directory of .dwt files to a directory of Jinja2 base templates'
    }

    def on_run(self, service, args, opts):
        if not os.path.exists(args[0]) or not os.path.isdir(args[0]):
            raise getopt.GetoptError('No such directory %r'%args[0])
        if not os.path.exists(args[1]) or not os.path.isdir(args[1]):
            raise getopt.GetoptError('No such directory %r'%args[1])
        for filename in os.listdir(args[0]):
            path = os.path.join(args[0], filename)
            if (not os.path.isdir(path)) and path.endswith(".dwt"):
                log.info('Converting %r', path)
                new_page = DreamweaverTemplateInstance(path)
                for name, value in new_page.items():
                    new_page[name] = '{% block '+name+' %}'+value+'{% endblock %}'
                for i, data in enumerate(new_page.template_regions):
                    new_page.template_regions[i] = self.escape(data)
                new_path = os.path.join(args[1], filename[:-4]+'.html')
                output = new_page.save_as_page(template_path='Templates/'+filename, new_path='Templates/'+filename)
                f=open(new_path, 'w')
                f.write(output.encode('utf-8'))
                f.close()

    def escape(self, data):
        for pair in []:
            data = data.replace(pair[0], pair[1])
        return data

