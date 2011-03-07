import datetime
import httplib2
import hashlib
import time
import re
import sys
from copy import deepcopy
from cStringIO import StringIO

from lxml import etree

from django.conf import settings
from django.db import IntegrityError
from django.utils.encoding import smart_str, smart_unicode

from player.crawler.models import CrawlerCollection, Report
from player.crawler.exceptions import CrawlerHttpException
from player.data.models import Collection, Item


def get_collection_link(crawler_collection):
    """
    This function will return a representative link to collection configured with
    the scrap tool.
    """
    return 'http://www.mozenda.com/console/#collections/%s/' % crawler_collection.collection_code


def get_collection_schema(collection_code):
    """
    This function will return the collection schema configured in your scrap tool
    with collection_code
    """
    params = [('Operation', 'Collection.GetFields'),
              ('CollectionID', collection_code)]
    response = _mozenda_request(params)

    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        fields = parser.findall('FieldList/Field')
        schema = {}
        for field in fields:
            field_name = field.find('Name').text
            field_id = field.find('FieldID').text
            field_is_system = field.find('IsSystem').text
            field_is_match_up = field.find('IsMatchUp').text
            schema[field_name] = {u'id': field_id,
                                  u'type': 'text',
                                  u'is_system': field_is_system,
                                  u'is_match_up': field_is_match_up}
        return schema


def load_collection_schema(crawler_collection):
    """
    This function will load the collection schema configured in your scrap tool
    with collection_code
    """
    schema = get_collection_schema(crawler_collection.collection_code)
    if schema:
        crawler_collection.schema = schema
        crawler_collection.save()


def has_new_data(crawler_collection):
    """ return True if scraping tool have new data to extract """
    collection_code = crawler_collection.collection_code
    last_job_time = crawler_collection.last_job_time
    if last_job_time is None:
        return True  # crawler never has extracted any data from mozenda
    mozenda_last_job_time = _get_last_job_time(collection_code)
    if mozenda_last_job_time is None:
        return False  # Mozenda never has launch any extraction Job
    if mozenda_last_job_time > last_job_time:
        return True  # Mozenda Job is newer than our data
    return False  # Mozenda Job is older


def extract_collection_data(crawler_collection):
    """
    This function will parse the collection as configured in your scrap tool.
    """
    collection_code = crawler_collection.collection_code
    # - Get view_id
    params = [('Operation', 'Collection.GetViews'),
              ('CollectionID', collection_code)]

    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        view_id = parser.find('ViewList/View/ViewID').text
    collections_to_extract = Collection.objects.filter(crawler_collection__collection_code=collection_code)

    params = [('Operation', 'View.GetItems'),
              ('ViewID', view_id)]

    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        nodes = parser.findall('ItemList/Item')
        items_dict = {'added': [], 'updated': [], 'deleted': []}
        for collection in collections_to_extract:
            items_extracted = []
            has_matchup_fields = collection.fields.is_mapped().filter(is_matchup=True).exists()
            for node in nodes:
                uid = hashlib.md5()
                field_dict = {}
                for field in collection.fields.all().is_mapped():
                    field_name = field.mapped_field
                    xml_field_name = field_name.replace(' ', '')
                    value = node.find(xml_field_name).text
                    if field.is_matchup or not has_matchup_fields:
                        uid.update(smart_str(value))
                    field_dict[field.slug] = value
                item = Item(uid=uid.hexdigest(), collection=collection)
                item.content = field_dict
                items_extracted.append(item)
                # note: the items are not save yet in database (only in memory)
                # when we confirm we passed the security thresholds, we will save them

            success, log, added_items, updated_items, deleted_items_uid, deleted_items = _collect_items_extracted(items_extracted, collection)
            collection.last_crawling_time = datetime.datetime.now()
            collection.save()
            items_dict['added'] += added_items
            items_dict['updated'] += updated_items
            items_dict['deleted'] += deleted_items
        crawler_collection.last_crawling_time = datetime.datetime.now()
        crawler_collection.last_job_time = _get_last_job_time(collection_code)
        crawler_collection.save()
        affected_collections = Collection.objects.filter(crawler_collection=crawler_collection)

        report = Report(
            crawler_collection=crawler_collection,
            crawling_time=crawler_collection.last_crawling_time,
        )
        report.deleted_items_json = items_dict['deleted']
        if success:
            report.return_code = 'suc'
            report.crawled_data = response[1]
            report.traceback = ''
        else:
            report.return_code = 'err'
            report.traceback = u'%s\n%s' % (smart_unicode(log.getvalue()), smart_unicode(response[1]))
            report.crawled_data = ''
        report.save()
        # adding items to report
        for item in items_dict['added']:
            report.added_items.add(item)
        for item in items_dict['updated']:
            report.updated_items.add(item)
    else:  # if response status code is not 200
        report = Report(
            crawler_collection=crawler_collection,
            crawling_time=datetime.datetime.now(),
        )
        report.return_code = 'err'
        report.traceback = str(response)
        report.crawled_data = ''
        report.save()


def get_collection_codes(login, password=None):
    """returns a list of tuples (code, label)

    username is actually the API key for Mozenda. It's called
    username to keep persistence between Mozenda and Dapper backend"""

    params = [('Operation', 'Collection.GetList')]
    response = _mozenda_request(params)

    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        cols_ids = parser.findall('CollectionList/Collection/CollectionID')
        cols_names = parser.findall('CollectionList/Collection/Name')

        collections = []
        for i in range(len(cols_ids)):
            aux_collection = (cols_ids[i].text, cols_names[i].text)
            collections.append(aux_collection)

        return collections
    # TODO: if the response code is not good, raise an exception


# ----- testing functions (used in unit tests) -----


def create_test_crawler_collection():
    """ Create test collection """
    return CrawlerCollection.objects.create(
            collection_code=settings.CRAWLER_TEST_COLLECTION_CODE,
    )


def run_test_extraction_process():
    """ Run extraction of test data in scraping tool """
    params = [('Operation', 'Agent.Run'),
              ('AgentID', settings.CRAWLER_TEST_AGENT_ID)]
    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        job_id = parser.findall('JobID')[0].text
        job_status = 'Running'
        job_status_params = [('Operation', 'Job.Get'),
                             ('JobID', job_id)]
        while job_status != 'Done':
            job_status_response = _mozenda_request(job_status_params)
            if job_status_response[0]['status'] == '200':
                job_status_parser = etree.fromstring(job_status_response[1])
                job_status = job_status_parser.findall('Job/Status')[0].text
                time.sleep(2)


# ----- auxiliar functions -----


def _get_last_job_time(collection_code):
    params = [('Operation', 'Agent.GetJobs'),
              ('AgentID', collection_code)]
    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        for job_status in parser.findall('JobList/Job'):
            if job_status.find('Status').text == 'Done':
                end_date_str = job_status.find('Ended').text
                return datetime.datetime.strptime(end_date_str, r'%Y-%m-%d %H:%M:%S')
    return None


def _build_url_query(api_key, params=[]):
    """build the url query string to perform a query to mozenda"""
    ops = ''
    for i in params:
        ops += '&%s=%s' % (i[0], i[1])

    url = '%s?WebServiceKey=%s&Service=Mozenda10%s'
    return url % (settings.CRAWLER_HOST, api_key, ops)


def _mozenda_request(params):
    http = httplib2.Http()

    response = http.request(_build_url_query(settings.CRAWLER_LOGIN, params))
    if response[0]['status'] == '200':
        return response
    else:
        raise CrawlerHttpException(response[0]['status'],
                                   response[1])


def _get_collection_id_from_code(collection_code):
    """returns the collection id from the collection code"""
    collections = get_collection_codes(settings.CRAWLER_LOGIN)

    for col in collections:
        if col[1] == collection_code:
            return col[0]

    return ''  # TODO: probably is a better idea to raise an exception


def _collect_items_extracted(items_list, collection):
    """returns a boolean value that is True if the extraction is
    correct, and False in other case"""

    # first, checks if it's the first crawling (no items on the collection)
    success = False
    log = StringIO()
    added_items = []
    updated_items = []
    deleted_items_uid = []
    deleted_items = []
    if collection.item_set.count() == 0:  # first crawl, store all items
        uid_list = []
        indexes_to_remove = []
        for i, item in enumerate(items_list):
            if item.uid not in uid_list:
                item.save()
                uid_list.append(item.uid)
            else:
                indexes_to_remove.append(i)
        removed_items = 0
        for i in indexes_to_remove:
            # we remove in a second step in order to mantain the loop iteration's
            del items_list[i - removed_items]
            removed_items += 1
        success = True
        print >> log, u'First crawling'
        added_items = items_list
    else:  # some elements are not
        # get how many items are new, updated and deleted from the "old" items
        dict_new_items = {}
        for item in items_list:
            dict_new_items[item.uid] = item
        previous_items_uid = []
        new_items_uid = []

        # it needs separates the UIDs and make the checks about it
        # because on the extracted Items, the __unicode__ function
        # does not work for us, because uses the id value, and it's
        # not enough to identify a single item.
        for item in Item.objects.all().filter(collection=collection):  # valids
            previous_items_uid.append(item.uid)

        for item in items_list:
            new_items_uid.append(item.uid)

        previous_items_uid_set = set(previous_items_uid)
        new_items_uid_set = set(new_items_uid)
        created_items_uid = list(new_items_uid_set.difference(previous_items_uid_set))
        deleted_items_uid = collection.crawler_collection.check_deleted and list(previous_items_uid_set.difference(new_items_uid_set)) or []

        for deleted_item_uid in deleted_items_uid:
            try:
                item = Item.objects.get(collection=collection, uid=deleted_item_uid,
                                        is_deleted=False, is_valid=True)
                deleted_items.append({'uid': deleted_item_uid,
                                      'repr': unicode(item),
                                      'collection': unicode(item.collection)})
            except Item.DoesNotExist:  # if the item does not exists, don't mind
                pass
        updated_items_uid = list(new_items_uid_set.intersection(previous_items_uid_set))

        aux = [uid for uid in updated_items_uid]
        for uid in aux:
            new_content = dict_new_items[uid].content
            if not Item.objects.get(collection=collection, uid=uid,
                                    is_deleted=False,
                                    is_valid=True).has_changed(new_content):
                updated_items_uid.remove(uid)

        # for now only checks as numeric values
        new_elements_threshold = _convert_threshold(collection.crawler_collection.new_elements_threshold)
        modified_elements_threshold = _convert_threshold(collection.crawler_collection.modified_elements_threshold)
        deleted_elements_threshold = _convert_threshold(collection.crawler_collection.deleted_elements_threshold)

        if new_elements_threshold < len(created_items_uid) or \
           modified_elements_threshold < len(updated_items_uid) or \
           deleted_elements_threshold < len(deleted_items_uid):
            if new_elements_threshold < len(created_items_uid):
                response = u'Too many new elements (%s/%s) in collection %s' % (
                    len(created_items_uid),
                    new_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            if modified_elements_threshold < len(updated_items_uid):
                response = u'Too many modified elements (%s/%s) in collection %s' % (
                    len(updated_items_uid),
                    modified_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            if modified_elements_threshold < len(deleted_items_uid):
                response = u'Too many deleted elements (%s/%s) in collection %s' % (
                    len(deleted_items_uid),
                    deleted_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            success = False
        else:
            success = True
            print >> log, u'Updated elements'

        # create new elements
        for uid in created_items_uid:
            item = dict_new_items[uid]
            item.is_valid = success
            try:
                item.save()
            except IntegrityError:
                item = Item.objects.get(uid=item.uid,
                                        collection=item.collection,
                                        is_valid=success)
            added_items.append(item)

        # update new elements
        for uid in updated_items_uid:
            item = Item.objects.get(uid=uid, collection=collection,
                                    is_deleted=False, is_valid=True)
            new_content = dict_new_items[uid].content
            if success:
                item.update_content(new_content)
                item.save()
            else:
                try:
                    invalid_item = Item.objects.get(uid=uid, collection=collection,
                                                    is_deleted=False, is_valid=False)
                except Item.DoesNotExist:
                    invalid_item = deepcopy(item)
                    invalid_item.id = None
                    invalid_item.is_valid = False

                invalid_item.update_content(new_content)
                invalid_item.save()

            updated_items.append(item)

        # delete obsoletes elements (if proceed)
        if collection.crawler_collection.check_deleted:
            for uid in deleted_items_uid:
                item = Item.objects.get(uid=uid, collection=collection,
                                        is_deleted=False, is_valid=True)
                if success:
                    item.delete()
                else:
                    try:
                        invalid_item = Item.objects.get(uid=uid, collection=collection,
                                                        is_deleted=False, is_valid=False)
                    except Item.DoesNotExist:
                        invalid_item = deepcopy(item)
                        invalid_item.id = None
                        invalid_item.is_valid = False

                    invalid_item.content = u''
                    invalid_item.save()

    return success, log, added_items, updated_items, deleted_items_uid, deleted_items


def _convert_threshold(value, total=None):
    """Returns an integer with the value. By now only checks
    integers, not percentages"""
    if not value:
        value = ''
    re_res = re.search('^\d+%$', value)
    if re_res != None:  # the expresion match, so remove the trailing '%'
        value = value[:-1]
    if value == '':
        return sys.maxint
    else:
        return int(value)
