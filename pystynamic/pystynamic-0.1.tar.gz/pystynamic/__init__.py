import os
import sys
import shutil

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

OUTPUT_PATH = '_output'
ENTITY_DIRECTORY = 'entities'
TEMPLATE_DIRECTORY = 'templates'

template_lookup = TemplateLookup(directories=[TEMPLATE_DIRECTORY])

class Context(object):
    pass

class RenderInfo(object):
    def __init__(self):
        self.template = None
        self.context = Context()

def build_site(site_module):
    entity_types = [x for x in dir(site_module) if not x.startswith('_')]
    known_entities = {}

    for entity_type in entity_types:
        setup_func = getattr(site_module, entity_type)
        entities = list(find_entities(entity_type, setup_func, known_entities))
        known_entities[entity_type] = [x.context for x in entities]

def find_entities(entity_type, setup_func, known_entities):
    possible_entity_filename = '%s.mako' % entity_type
    possible_entity_directory = os.path.join(ENTITY_DIRECTORY, entity_type)

    try:
        entity_source = entity_source_lookup.get_template(possible_entity_filename)
        yield build_entity_build_info(entity_source, setup_func, known_entities)
    except TopLevelLookupException as e:
        if not os.path.isdir(possible_entity_directory):
            raise Exception('Could not find any entity type "%s"' % entity_type)
        filenames = os.listdir(possible_entity_directory)
        entity_filenames = filter(lambda x: not x.startswith('_') and x.endswith('.mako'), filenames)
        if len(entity_filenames) == 0:
            raise Exception('Could not find any entity type "%s" in directory "%s"' % (entity_type, possible_entity_directory))

        for entity_filename in entity_filenames:
            entity_name = entity_filename[:-len('.mako')]
            full_entity_filename = os.path.join(entity_type, entity_filename)
            entity_source = entity_source_lookup.get_template(full_entity_filename)
            yield build_entity_build_info(entity_source, setup_func, known_entities)

class EntityBuildInfo(object):
    def __init__(self, entity, render_info):
        self.entity = entity
        self.render_info = render_info

def build_entity_build_info(entity, setup_func, known_entities):
    context = Context()
    setup_func(known_entities, context)
    return EntityBuildInfo(known_entities, render_info)
        

if __name__ == '__main__':
    output_path_copy = os.path.join(OUTPUT_PATH, 'static')
    shutil.rmtree(output_path_copy, ignore_errors=True)
    shutil.copytree('static', output_path_copy)

    import website
    build_site(website)
