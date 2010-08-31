"""
Routines that integrate the basic object classes.

Things like loading up all the tiddlers in a recipe,
listing tiddlers in a bag, and filtering tiddlers.

These are kept in here to avoid a having store
and serialize objects in filters and recipes and the
like.
"""

import logging

from tiddlyweb.model.bag import Bag
from tiddlyweb.filters import (FilterIndexRefused, parse_for_filters,
        recursive_filter)
from tiddlyweb.store import NoBagError


def get_tiddlers_from_recipe(recipe, environ=None):
    """
    Return the list of tiddlers that result
    from processing the recipe.

    This list of tiddlers is unique by title with
    tiddlers later in the recipe taking precedence
    over those earlier in the recipe.
    """

    template = recipe_template(environ)
    store = recipe.store
    uniquifier = {}
    for bag, filter_string in recipe.get_recipe(template):
        if isinstance(bag, basestring):
            bag = Bag(name=bag)
        bag.store = store
        for tiddler in _filter_tiddlers_from_bag(bag, filter_string,
                environ=environ):
            uniquifier[tiddler.title] = tiddler
    return uniquifier.values()


def determine_bag_from_recipe(recipe, tiddler, environ=None):
    """
    We have a recipe and a tiddler. We need to
    know the bag in which this tiddler can be found.
    This is different from determine_bag_for_tiddler().
    That one finds the bag the tiddler _could_ be in.
    This is the bag the tiddler _is_ in.

    We reverse the recipe_list, and filter each bag
    according to the rule. Then we look in the list of
    tiddlers and see if ours is in there.
    """
    store = recipe.store
    template = recipe_template(environ)
    try:
        indexer = environ.get('tiddlyweb.config', {}).get('indexer', None)
        if indexer:
            index_module = __import__(indexer, {}, {}, ['index_query'])
        else:
            index_module = None
    except (AttributeError, KeyError):
        index_module = None

    for bag, filter_string in reversed(recipe.get_recipe(template)):
        bag = _look_for_tiddler_in_bag(tiddler, bag,
                filter_string, environ, store, index_module)
        if bag:
            return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def _look_for_tiddler_in_bag(tiddler, bag, filter_string,
        environ, store, index_module):
    """
    Look up the indicated tiddler in a bag, filtered by filter_string.
    """
    if isinstance(bag, basestring):
        bag = Bag(name=bag)
    if store:
        bag = store.get(bag)

    def _query_index(bag):
        """
        Try looking in an available index to see if the tiddler exists.
        """
        kwords = {'id': '%s:%s' % (bag.name, tiddler.title)}
        tiddlers = index_module.index_query(environ, **kwords)
        if list(tiddlers):
            logging.debug('satisfied recipe bag query via filter index')
            return bag
        return None

    def _query_bag(bag):
        """
        Look in a bag to see if tiddler is in there.
        """
        for candidate_tiddler in _filter_tiddlers_from_bag(bag,
                filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                return bag
        return None

    if not filter_string and index_module:
        try:
            found_bag = _query_index(bag)
        except FilterIndexRefused:
            logging.debug('determined bag filter refused')
            found_bag = _query_bag(bag)
        if found_bag:
            return bag
    else:
        found_bag = _query_bag(bag)
        if found_bag:
            return found_bag

    return None


def determine_bag_for_tiddler(recipe, tiddler, environ=None):
    """
    Return the bag which this tiddler would be in if we
    were to save it to the recipe rather than to a default
    bag.

    This is a matter of reversing the recipe list and seeing
    if the tiddler is a part of the bag + filter. If bag+filter
    is true, return that bag.
    """
    template = recipe_template(environ)
    for bag, filter_string in reversed(recipe.get_recipe(template)):
        # ignore the bag and make a new bag
        for candidate_tiddler in filter_tiddlers([tiddler],
                filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                if isinstance(bag, basestring):
                    bag = Bag(name=bag)
                return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def get_tiddlers_from_bag(bag):
    """
    Return the list of tiddlers that are in a bag.
    """
    for tiddler in bag.store.list_bag_tiddlers(bag):
        yield tiddler


def filter_tiddlers(tiddlers, filters, environ=None):
    """
    Return a generator of tiddlers resulting from
    filtering the provided iterator of tiddlers by
    the provided filters.

    If filters is a string, it will be parsed for
    filters.
    """
    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, tiddlers)


def _filter_tiddlers_from_bag(bag, filters, environ=None):
    """
    Return the list of tiddlers resulting from filtering
    bag by filter. The filter is a string that will be
    parsed to a list of filters.
    """
    indexable = bag

    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, bag.store.list_bag_tiddlers(bag),
            indexable=indexable)


def recipe_template(environ):
    """
    provide a means to specify custom {{ key }} values in recipes
    which are then replaced with the value specified in
    environ['tiddlyweb.recipe_template']
    """
    template = {}
    if environ:
        template = environ.get('tiddlyweb.recipe_template', {})
        try:
            template['user'] = environ['tiddlyweb.usersign']['name']
        except KeyError:
            pass

    return template
