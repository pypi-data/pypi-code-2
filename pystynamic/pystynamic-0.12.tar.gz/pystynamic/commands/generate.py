import os
import errno
import shutil
import logging

from pystynamic.generation import SiteGenerator

logger = logging.getLogger('pystynamic')

def generate_command(site_directory, output_directory, force=False):
    if os.path.exists(output_directory):
        if not force:
            while True:
                try:
                    msg = 'Note: This will delete the directory {0}. Are you sure you want to do this? [yes/no] '.format(output_directory)
                    result = raw_input(msg)
                except KeyboardInterrupt:
                    print '\n' # Just trying to help with the command-line prettiness.
                    raise

                if result.lower() in ['yes', 'no']:
                    break

            if result == 'no':
                print 'Generation cancelled'
                return

        shutil.rmtree(output_directory)

    site_generator = SiteGenerator.build_for_path(site_directory)
    for page, result in site_generator.generate_all():
        rel_page = page[1:]
        # Special case for home page
        if rel_page == '':
            full_filename = os.path.join(output_directory, 'index.html')
            directory_path = output_directory
        else:
            # Add the .html if there doesn't appear to be an extension.
            if '.' not in rel_page:
                rel_page = rel_page + '.html'
            full_filename = os.path.join(output_directory, rel_page)
            directory_path = os.path.dirname(full_filename)

        try:
            os.makedirs(directory_path)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass

        logger.debug('Creating file "{0}"'.format(full_filename))
        with open(full_filename, 'w') as f:
            f.write(result)

    # Copy over the static files
    shutil.copytree(os.path.join(site_directory, 'static'), os.path.join(output_directory, 'static'))

