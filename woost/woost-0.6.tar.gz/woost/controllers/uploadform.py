#-*- coding: utf-8 -*-
u"""Provides the `UploadForm` class, that makes it easy to upload files into
`woost.models.File` objects.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from tempfile import mkdtemp
from shutil import move, rmtree
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers import Form, FileUpload
from woost.models import File


class UploadForm(Form):

    @cached_getter
    def upload_members(self):
        return [member
                for member in self.model.members().itervalues()
                if isinstance(member, schema.Reference)
                and issubclass(member.type, File)]

    @cached_getter
    def adapter(self):
        adapter = Form.adapter(self)

        for member in self.upload_members:
            key = member.name
            adapter.export_rules.add_rule(self.ExportUploadInfo(self, key))
            adapter.import_rules.add_rule(self.ImportUploadInfo(self, key))

        return adapter

    class ExportUploadInfo(schema.Rule):

        def __init__(self, form, key):
            self.form = form
            self.key = key

        def adapt_schema(self, context):

            if context.consume(self.key):
                source_member = context.source_schema[self.key]
                target_member = FileUpload(self.key,
                    required = source_member.required,
                    member_group = source_member.member_group,
                    hash_algorithm = "md5",
                    get_file_destination = lambda upload:
                        self.form.get_temp_upload_filename(source_member)
                )
                target_member.adaptation_source = source_member
                target_member.copy_source = source_member
                context.target_schema.add_member(target_member)

        def adapt_object(self, context):            
            if context.consume(self.key):
                file = context.get(self.key)                
                if file:
                    context.set(self.key, {
                        "file_name": file.file_name,
                        "mime_type": file.mime_type,
                        "file_size": file.file_size,
                        "file_hash": file.file_hash
                    })

    class ImportUploadInfo(schema.Rule):

        def __init__(self, form, key):
            self.form = form
            self.key = key

        def adapt_object(self, context):
            if context.consume(self.key):            
                upload = context.get(self.key, None)                
                if upload:
                    file = self.form.get_file(self.form.model[self.key])
                    file.file_name = upload["file_name"]
                    file.mime_type = upload["mime_type"]
                    file.file_size = upload["file_size"]
                    file.file_hash = upload["file_hash"]

    def submit(self):
        Form.submit(self)
        self.upload()

    @cached_getter
    def temp_upload_folder(self):
        return mkdtemp()

    def get_temp_upload_filename(self, member):
        return os.path.join(
            self.temp_upload_folder,
            member.name
        )

    def get_file(self, member):
        instance = self.instance
        file = schema.get(instance, member.name, default = None)

        if file is None:
            file = self.create_file(member)
            schema.set(instance, member.name, file)

        return file

    def create_file(self, member):
        return member.type()

    def upload(self):

        # Move uploaded files to their permanent location
        try:
            for member in self.upload_members:
                
                file = schema.get(self.instance, member)
                temp_file = self.get_temp_upload_filename(member)

                if file and os.path.exists(temp_file):
                    
                    dest = file.file_path

                    if os.path.exists(dest):
                        os.remove(dest)

                    move(temp_file, dest)

        # Remove the temporary folder
        finally:
            rmtree(self.temp_upload_folder)

