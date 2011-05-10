# -*- coding: utf-8 -*-


# Podis -- Retrieve INSEE codes of french communes from their postal distributions
# By: Romain Soufflet <rsoufflet@easter-eggs.com>
#
# Copyright (C) 2010 Easter-eggs
#
# This file is part of Podis.
#
# Podis is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Podis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""The application's programming interface."""


import logging
import datetime
from operator import itemgetter
import re

import pymongo

import podis
from . import lib


__all__ = ['autocomplete', 'find_postal_distribution', 'get_routes', 'guess_territory', 'register_route', 'retrieve_territory']


log = logging.getLogger(__name__)
bounding_territories_kinds = {
    "ArrondissementOfFrance": "arrondissement_code",
    "CantonOfFrance": "canton_code",
    "CommuneOfFrance": "commune_code",
    "DepartmentOfFrance": "department_code",
    "IntercommunalityOfFrance": "intercommunality_code",
    "OverseasCollectivityOfFrance": "overseas_code",
    "PaysOfFrance": "pays_code",
    "RegionOfFrance": "region_code",
    "RegionalNatureParkOfFrance": "regional_nature_park_code" ,
    }


def autocomplete(route_distribution, bounding_territory = None, unique = False, kinds = None, limit = 10, offset = 0):
    """Autocomplete the route_distribution entered by user"""
    return [
        dict(
            value = territory_insee_code,
            label = "%s %s" % (territory_common_code, territory_name) \
                    if territory_common_code and territory_name else territory_common_code or territory_name,
            kind = kind,
            )
        for territory_insee_code, kind, territory_common_code, simple_name, territory_name
            in iter_autocompleter_routes(route_distribution, bounding_territory = bounding_territory, unique = unique, kinds = kinds, limit = limit, offset = offset)
        ]


def count_results(route_distribution, bounding_territory = None, unique = False, kinds = None):
    """Count total number of result for a request (usefull for pagers)"""
    # Split route_distribution to separate common_code and route_name
    common_code, route_name = split_route_distribution(route_distribution)
    simple_name = lib.simplify_route_name(route_name)

    condition = {}
    if simple_name is None and common_code is None:
        condition['population'] = {'$gt': 100000}
        condition['pobox_ratio'] = {'$ne': 1}
    if common_code is not None:
        condition['common_code'] = re.compile("^%s" % re.escape(common_code))
    if simple_name is not None:
        if len(simple_name) <= 3:
            condition['simple_name'] = re.compile("^%s" % re.escape(simple_name))
        else:
            simple_words = simple_name.split()
            condition['simple_words'] = {'$all': [
                re.compile("^%s" % re.escape(word))
                for word in simple_words
                ]}
    if bounding_territory is not None:
        assert isinstance(bounding_territory, dict)
        condition["bounding_territories"] = {"$elemMatch": {
            "kind": bounding_territory["kind"],
            "code": bounding_territory["code"],
            }}

    if kinds is not None:
        if isinstance(kinds, basestring):
            condition['territory.kind'] = kinds
        elif len(kinds) == 1 and isinstance(kinds[0], basestring):
            condition['territory.kind'] = kinds[0]
        else:
            condition['territory.kind'] = {'$in': kinds}
    if unique:
        return len(podis.db[podis.collection_name].find(condition).distinct("territory"))
    return podis.db[podis.collection_name].find(condition).count()


def delete_obsolete_routes(author, routes_key):
    assert author is not None
    author = unicode(author)
    collection = podis.db[podis.collection_name]
    deleted = False
    if routes_key:
        for territory_kind, territory_code, common_code, simple_name in routes_key:
            route = collection.find_one({
                'common_code': common_code,
                'simple_name': simple_name,
                'territory.code': territory_code,
                'territory.kind': territory_kind,
                })
            if route is not None:
                for variant in route['variants'][:]:
                    for ballot in variant['ballots'][:]:
                        if ballot['author'] == author:
                            variant['ballots'].pop(variant['ballots'].index(ballot))
                        if not variant['ballots']:
                            route['variants'].pop(route['variants'].index(variant))
                if route['variants']:
                    collection.save(route, safe = True)
                else:
                    collection.remove(dict(_id = route['_id']))
                deleted = True
    return deleted


def find_postal_distribution(territory):
    """Retrieve the "best" postal distribution of a territory """
    assert isinstance(territory, dict)
    condition = {"territory": territory}

    cursor = podis.db[podis.collection_name].find(condition)
    cursor.sort([
        ('highest_score', pymongo.DESCENDING),
        ('pobox_ratio', pymongo.ASCENDING),
        ('population', pymongo.DESCENDING),
        ('simple_name', pymongo.ASCENDING),
        ('common_code', pymongo.ASCENDING),
        ])
    if cursor.count() == 0:
        return None
    else:
        document = cursor.next()
        names = [variant["name"] for variant in document["variants"]]
        names.sort()

        return dict (
            common_code = document["common_code"],
            name = names.pop(),
            )


def get_existing_routes_key(author):
    assert author is not None
    author = unicode(author)
    condition = {'variants.ballots.author': author}
    fields = {'territory.kind': True, 'territory.code': True, 'common_code': True, 'simple_name': True, }
    return set(
        (
            route['territory']['kind'],
            route['territory']['code'],
            route.get('common_code'),
            route['simple_name'],
            )
        for route in podis.db[podis.collection_name].find(condition, fields)
        )


def get_routes(route_distribution, bounding_territory = None, unique = False, kinds = None, limit = 10, offset = 0):
    """Return the maximum of corresponding routes"""
    return [
        dict(
            score = score,
            territory_kind = territory_kind,
            territory_code = territory_code,
            pobox = pobox,
            common_code = common_code,
            variant_name = variant_name,
            simple_name = simple_name,
            ballots = ballots,
            )
        for score, territory_kind, territory_code, pobox, common_code, variant_name, simple_name, ballots
            in iter_routes(route_distribution, bounding_territory = bounding_territory, unique = unique, kinds = kinds, limit = limit, offset = offset)
        ]


def guess_territory(route_distribution, bounding_territory = None, territories  = None, kinds = None):
    """Deduce a territory code and kind from a common code and/or name.

    Three functions try to guarantee as much as possible that the returned common_code is the good one.
    """
    common_code, route_name = split_route_distribution(route_distribution)
    simple_name = lib.simplify_route_name(route_name)

    condition = {}
    if territories is not None:
        condition['territory'] = {'$in': [dict(
                kind = kind,
                code = code,
                )
            for kind, code in territories
            ]}
    if bounding_territory is not None:
        assert isinstance(bounding_territory, dict)
        condition["bounding_territories"] = {"$elemMatch": {
            "kind": bounding_territory["kind"],
            "code": bounding_territory["code"],
            }}
    if kinds is not None:
        if isinstance(kinds, basestring):
            condition['territory.kind'] = kinds
        elif len(kinds) == 1 and isinstance(kinds[0], basestring):
            condition['territory.kind'] = kinds[0]
        else:
            condition['territory.kind'] = {'$in': kinds}
    for condition in iter_condition(condition, common_code, simple_name):
        route_candidates = podis.db[podis.collection_name].find(condition)
        if route_candidates.count() == 1:
            return route_candidates[0]['territory']
        elif route_candidates.count() > 1:
            territory = None
            for route in route_candidates:
                if territory is None:
                    territory = route['territory']
                elif route['territory'] != territory:
                    break
            else:
                assert territory is not None
                return territory
    return None


def iter_autocompleter_routes(route_distribution, bounding_territory = None, unique = False, kinds = None, limit = 10, offset = 0):
    """Iterate over routes that match the partial route_distribution typed by user in autocompleter"""
    # Split route_distribution to separate common_code and route_name
    common_code, route_name = split_route_distribution(route_distribution)
    simple_name = lib.simplify_route_name(route_name)

    condition = {}
    if simple_name is None and common_code is None:
        condition['population'] = {'$gt': 100000}
        condition['pobox_ratio'] = {'$ne': 1}
    if common_code is not None:
        condition['common_code'] = re.compile("^%s" % re.escape(common_code))
    if simple_name is not None:
        if len(simple_name) <= 3:
            condition['simple_name'] = re.compile("^%s" % re.escape(simple_name))
        else:
            simple_words = simple_name.split()
            condition['simple_words'] = {'$all': [
                re.compile("^%s" % re.escape(word))
                for word in simple_words
                ]}
    if bounding_territory is not None:
        assert isinstance(bounding_territory, dict)
        condition["bounding_territories"] = {"$elemMatch": {
            "kind": bounding_territory["kind"],
            "code": bounding_territory["code"],
            }}
    if kinds is not None:
        if isinstance(kinds, basestring):
            condition['territory.kind'] = kinds
        elif len(kinds) == 1 and isinstance(kinds[0], basestring):
            condition['territory.kind'] = kinds[0]
        else:
            condition['territory.kind'] = {'$in': kinds}
    if limit is None:
        limit = 10
    assert isinstance(limit, int)
    cursor = podis.db[podis.collection_name].find(condition)
    # Sort fails sometimes with error: OperationFailure: database error: too much data for sort() with no index
    cursor.sort([
        ('highest_score', pymongo.DESCENDING),
        ('pobox_ratio', pymongo.ASCENDING),
        ('population', pymongo.DESCENDING),
        ('simple_name', pymongo.ASCENDING),
        ('common_code', pymongo.ASCENDING),
        ])
#    cursor = sorted(cursor, key = lambda route: (
#        -route.get('highest_score', 0),
#        route.get('pobox_ratio'),
#        -route.get('population', 0), # descending
#        route.get('simple_name'),
#        route.get('common_code'),
#       ))

    encountered = set()
    for route in cursor:
        if (route['territory']['kind'], route['territory']['code']) not in encountered:
            if offset > 0:
                offset = offset - 1
            else:
                max_variant = max(route['variants'], key = itemgetter('score')) if len(route['variants']) > 0 else None
                max_variant_name = max_variant['name'] if max_variant is not None else ''
                yield route['territory']['code'], route['territory']['kind'], route.get('common_code'), route['simple_name'],\
                        max_variant_name
                limit -= 1
        if unique:
            encountered.add((route['territory']['kind'], route['territory']['code']))

        if limit <= 0:
            break


def iter_condition(condition, common_code, simple_name):
    # Try using both code and simple name fragments.
    for code_condition in iter_condition_by_common_code(condition, common_code):
        for route_name_condition in iter_condition_by_route_name(code_condition, simple_name):
            yield route_name_condition
    # Next, try with only simple name fragments.
    condition.pop('common_code', None)
    for route_name_condition in iter_condition_by_route_name(condition, simple_name):
        yield route_name_condition
    # Then, try with only code fragments.
    condition.pop('simple_words', None)
    for code_condition in iter_condition_by_common_code(condition, common_code):
        yield code_condition
    # Finally, try without filters based on postal distribution.
    yield condition


def iter_condition_by_common_code(condition, code):
    if code:
        if len(code) == 5:
            condition['common_code'] = code
            yield condition
        else:
            condition['common_code'] = re.compile('^%s' % re.escape(code))
            yield condition
        if code.startswith(('97', '98')):
            if len(code) > 3:
                condition['common_code'] = re.compile('^%s' % re.escape(code[:3]))
                yield condition
        elif len(code) > 2:
            condition['common_code'] = re.compile('^%s' % re.escape(code[:2]))
            yield condition

def iter_condition_by_route_name(condition, simple_name):
    if simple_name:
        # First retrieve routes routings that are not different from given one.
        condition['simple_name'] = simple_name
        yield condition
        del condition['simple_name']

        # Then retrieve routes routings that are not very different from given one.
        condition['$where'] = "levenshtein(this.simple_name, '%s') < 3" % simple_name
        yield condition
        del condition['$where']

        for split_simple_name in iter_simple_names(simple_name):
            # Then retrieve postal routings containing given words.
            filtered_condition = condition
            filtered_condition['simple_words'] = {}
            filtered_condition['simple_words']['$all'] = []
            for simple_word in split_simple_name:
                filtered_condition['simple_words']['$all'].append(re.compile('^%s' % re.escape(simple_word)))
            yield filtered_condition


def iter_routes(route_distribution, bounding_territory = None, unique = False, kinds = None, limit = 10, offset = 0):
    """Iterate over the maximum number of routes that could match the route_distribution"""
    # Split route_distribution to separate common_code and route_name
    common_code, route_name = split_route_distribution(route_distribution)
    simple_name = lib.simplify_route_name(route_name)

    condition = {}
    if simple_name is None and common_code is None:
        condition['population'] = {'$gt': 100000}
        condition['pobox_ratio'] = {'$ne': 1}
    if common_code is not None:
        condition['common_code'] = re.compile("^%s" % re.escape(common_code))
    if simple_name is not None:
        if len(simple_name) <= 3:
            condition['simple_name'] = re.compile("^%s" % re.escape(simple_name))
        else:
            simple_words = simple_name.split()
            condition['simple_words'] = {'$all': [
                re.compile("^%s" % re.escape(word))
                for word in simple_words
                ]}
    if bounding_territory is not None:
        assert isinstance(bounding_territory, dict)
        condition["bounding_territories"] = {"$elemMatch": {
            "kind": bounding_territory["kind"],
            "code": bounding_territory["code"],
            }}
    if kinds is not None:
        if isinstance(kinds, basestring):
            condition['territory.kind'] = kinds
        elif len(kinds) == 1 and isinstance(kinds[0], basestring):
            condition['territory.kind'] = kinds[0]
        else:
            condition['territory.kind'] = {'$in': kinds}
    if limit is None:
        limit = 10
    assert isinstance(limit, int)
    cursor = podis.db[podis.collection_name].find(condition)
    # Sort fails sometimes with error: OperationFailure: database error: too much data for sort() with no index
    cursor.sort([
        ('highest_score', pymongo.DESCENDING),
        ('pobox_ratio', pymongo.ASCENDING),
        ('population', pymongo.DESCENDING),
        ('simple_name', pymongo.ASCENDING),
        ('common_code', pymongo.ASCENDING),
        ])
#    cursor = sorted(cursor, key = lambda route: (
#        -route.get('highest_score', 0),
#        route.get('pobox_ratio'),
#        -route.get('population', 0), # descending
#        route.get('simple_name'),
#        route.get('common_code'),
#       ))

    encountered = set()
    for route in cursor:
        if (route['territory']['kind'], route['territory']['code']) not in encountered:
            if offset > 0:
                offset = offset - 1
            else:
                variant = max(route['variants'], key = itemgetter('score')) if len(route['variants']) > 0 else None
                variant_name = variant['name'] if variant is not None else ''
                yield (
                    variant['score'],
                    route['territory']['kind'],
                    route['territory']['code'],
                    variant.has_key('pobox'),
                    route.get('common_code'),
                    variant_name,
                    route['simple_name'],
                    variant['ballots'],
                    )
                limit -= 1
        if unique:
            encountered.add((route['territory']['kind'], route['territory']['code']))
        if limit <= 0:
            break


def iter_simple_names(simple_name):
    split_simple_name = simple_name.split()
    yield split_simple_name
    if 'CEDEX' in split_simple_name:
        del split_simple_name[split_simple_name.index('CEDEX'):]
        yield split_simple_name
    while len(split_simple_name) > 1:
        del split_simple_name[-1]
        yield split_simple_name


def register_route(author = None, date = None, mark = 1, territory = None, existing_routes_key = None,
                   pobox = None, common_code = None, route_name = None):
    """Record or update a route"""
    assert author is not None
    author = unicode(author)
    if date is None:
        date = datetime.datetime.now()
    else:
        assert isinstance(date, datetime.datetime)
    if mark is None:
        mark = 0
    else:
        assert mark in (1, 0, -1)
    assert territory is not None
    assert isinstance(territory, dict)
    if pobox is not None:
        pobox = bool(pobox)
    if common_code is not None:
        assert isinstance(common_code, basestring)
    if territory['kind'] in [u'ArrondissementOfCommuneOfFrance', u'AssociatedCommuneOfFrance', u'CommuneOfFrance']:
        if territory['code'] == '13055' and common_code in (None, '13', '13000'):
            log.warning('Wrong depcom %s for postal distribution %s %s. It should be an arrondissement of Marseille' % (
                territory['code'], common_code, route_name))
            common_code = "13000"
        elif territory['code'] == '69123' and common_code in (None, '69', '69000'):
            log.warning('Wrong depcom %s for postal distribution %s %s. It should be an arrondissement of Lyon' % (
                territory['code'], common_code, route_name))
            common_code = "69000"
        elif territory['code'] == '75056' and common_code in (None, '75', '75000'):
            log.warning('Wrong depcom %s for postal distribution %s %s. It should be an arrondissement of Paris' % (
                territory['code'], common_code, route_name))
            common_code = "75000"
    assert isinstance(route_name, basestring)
    simple_name = lib.simplify_route_name(route_name)
    simple_words = set()
    if simple_name:
        simple_words = set(simple_name.split())
        simple_words.add(common_code)
        if pobox is None and simple_words.intersection(['ARMEE', 'ARMEES', 'CEDEX', 'UNIVERSITE', 'UNIVERSITES']):
            pobox = True
    else:
        simple_name = None

    # Test if the document already existe
    route = podis.db[podis.collection_name].find_one({
        'common_code': common_code,
        'territory': territory,
        'simple_name': simple_name,
        })
    # if no document matches, create it
    if route is None:
        # Get another route with the same territory kind and code to find the population attribute
        population = podis.db[podis.collection_name].find_one({'territory': territory}).get('population')
        route = dict(
            common_code = common_code,
            territory = territory,
            variants = [dict(
                name = route_name,
                ballots = [],
                )],
            simple_name = simple_name,
            simple_words = list(simple_words),
            )
        if pobox:
            route['variants'][0]['pobox'] = 1
        if population:
            route['population'] = population
    # if route already exist, just update fields, else ceeate it
    exist = False
    for variant in route['variants']:
        if variant['name'] == route_name:
            exist = True
            break
    if exist == True:
        for ballot in variant['ballots']:
            if author == ballot['author']:
                variant['ballots'].remove(ballot)
    else:
        variant = dict(
            name = route_name,
            ballots = [],
            )
        route['variants'].append(variant)
    ballot = dict(
        author = author,
        timestamp = date,
        mark = mark,
        )
    variant['ballots'].append(ballot)
    score_numerator = 0
    for ballot in variant['ballots']:
        if ballot['mark'] == 1:
            score_numerator += 1
        if ballot['mark'] == -1:
            score_numerator -= 1
    score_denominator = len(variant['ballots'])
    variant['score'] = score_numerator / score_denominator

    if pobox is not None and pobox == True:
        variant['pobox'] = True
    elif pobox is None and variant.get('pobox', False):
        del variant['pobox']
    nb_pobox = 0
    highest_score = None
    for variant in route['variants']:
        if variant.has_key('pobox'):
            nb_pobox += 1
        if highest_score is None or variant['score'] > highest_score:
            highest_score = variant['score']
    if len(route['variants']) > 0:
        route['pobox_ratio'] = nb_pobox / len(route['variants'])
        route['highest_score'] = highest_score
    else:
        route['pobox_ratio'] = 1

    # store new value
    podis.db[podis.collection_name].save(route, safe = True)
    if existing_routes_key is not None:
        existing_routes_key.discard((route['territory']['kind'], route['territory']['code'], route.get('common_code'), route['simple_name']))
    return True


def retrieve_territory(route_distribution, bounding_territory = None, territories = None, kinds = None, existing_routes_key = None):
    """Retrieve the territory from a route_distribution(common_code and route_name)."""
    common_code, route_name = split_route_distribution(route_distribution)
    condition = {}
    if common_code is not None:
        assert isinstance(common_code, basestring)
        condition['common_code'] = common_code
    if territories is not None:
        condition['territory'] = {'$in': [dict(
                kind = kind,
                code = code,
                )
            for kind, code in territories
            ]}
    if bounding_territory is not None:
        assert isinstance(bounding_territory, dict)
        condition["bounding_territories"] = {"$elemMatch": {
            "kind": bounding_territory["kind"],
            "code": bounding_territory["code"],
            }}
    if route_name is None:
        simple_name = None
    else:
        simple_name = lib.simplify_route_name(route_name)
        condition['simple_name'] = simple_name
    if kinds is not None:
        if isinstance(kinds, basestring):
            condition['territory.kind'] = kinds
        elif len(kinds) == 1 and isinstance(kinds[0], basestring):
            condition['territory.kind'] = kinds[0]
        else:
            condition['territory.kind'] = {'$in': kinds}
    route = podis.db[podis.collection_name].group(
        key = {
            'territory.code': True,
            'simple_name': True,
            'territory.kind': False,
            },
        condition = condition,
        reduce = """function(obj,prev){prev.nb += 1;}""",
        initial = {'nb': 0})
    if len(route) != 1:
        return None
    route = route[0]
    if existing_routes_key is not None:
        existing_routes_key.discard((
            route['territory.kind'],
            route['territory.code'],
            route.get('common_code'),
            route['simple_name'],
            ))
    return dict(
        kind = route['territory.kind'],
        code = route['territory.code'],
        )


def split_route_distribution(route_distribution):
    """Separate the postal distribution into a pair (postal code, postal routing)"""
    if route_distribution is None:
        return None, None
    route_distribution = unicode(route_distribution)
    common_code_re = re.compile(r'\d[-\w]')
    common_code_words = []
    route_name_words = []
    for word in route_distribution.split():
        if not route_name_words and common_code_re.match(word):
            common_code_words.append(word)
        else:
            route_name_words.append(word)
    return u''.join(common_code_words) or None, u' '.join(route_name_words) or None

