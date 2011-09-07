import os, sys
import shutil

from hurry.tinymce.download import download_tinymce, download_language

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: tinymceprepare <tinyMCE version>"
        return

    # download tinymce library into package
    package_dir = os.path.dirname(__file__)
    dest_path = os.path.join(package_dir, 'tinymce-build')

    # remove previous tinymce
    shutil.rmtree(dest_path, ignore_errors=True)

    def copy_tinymce(ex_path):
        """Copy to location 'tinymce-build' in package."""
        build_path = os.path.join(ex_path, 'tinymce', 'jscripts', 'tiny_mce')
        if not os.path.exists(build_path):
            # Some versions of tinyMCE are packaged without a
            # top-level ``tinymce`` directory.
            build_path = os.path.join(ex_path, 'jscripts', 'tiny_mce')
        shutil.copytree(build_path, dest_path)

    def copy_language(ex_path):
        """Copy language files to 'tinymce-build' in package."""
        base_path = os.path.join(ex_path, 'tinymce_language_pack')
        for path, folders, files in os.walk(base_path):
            for filename in files:
                source = os.path.join(path, filename)
                # source contains seperator, so is.path.join does not help us
                # here
                target = dest_path + source.replace(base_path, '')
                shutil.copy(source, target)

    download_tinymce(version, copy_tinymce)
    download_language('de', copy_language)
