import os

from dbtemplates.models import Template

from staging.backends.base import StagingBackend


class TemplateStagingBackend(StagingBackend):

    def _get_template_filename(self, template):
        return os.path.join(self.path, template.name)

    def export_to_staging(self):
        for template in Template.objects.all():
            template_file = self._get_template_filename(template)
            template_dir = os.path.dirname(template_file)
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
            fp = open(template_file, 'w')
            fp.write(template.content)
            fp.close()

    def import_from_staging(self):
        for root, dirs, files in os.walk(self.path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                template_name = os.path.join(root[len(self.path) + 1:], file_name)
                content = open(file_path).read()
                tpl, created = Template.objects.get_or_create(name=template_name)
                tpl.content = content
                tpl.save()
