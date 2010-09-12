#!/usr/bin/env python
# Copyright 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
GABI: Google Address Book Importer
"""

__author__ = 'Lorenzo Gil Sanchez'
__email__ = 'lorenzo.gil.sanchez@gmail.com'
__license__ = 'GPL 3'
__version__ = '0.1.0'

import getpass
import json
import optparse
import os.path
import sys
import time

import gdata.client
import gdata.contacts.client


class ContactsImporter(object):
    """Google Contacts client that fetches contacts using the GData library."""

    singlevalue_attributes = (
        ('title', 'text'),
        ('birthday', 'when'),
        ('nickname', 'text'),
        ('organization', 'name.text'),
        ('updated', 'text'),
        )

    multivalue_attributes = (
        ('email', 'address'),
        ('phone_number', 'text'),
        ('postal_address', 'text'),
        ('website', 'href'),
        )

    def __init__(self, user, password=None, verbose=False):
        """Constructor.

        Arguments:
          user: email of the Google Account
          password: password for the Google Account. If none is supplied, the
                    constructor will ask the user with the getpass function
          verbose: whether to print verbose output in the other methods.
        """
        self.client = gdata.contacts.client.ContactsClient()
        if not password:
            prompt = 'Enter the password for the %s account: ' % user
            password = getpass.getpass(prompt)
        self.client.client_login(user, password, 'gabi')
        self.verbose = verbose

    def sync(self, updated_min=None):
        """Return the contacts in the Google Account defined in the constructor

        Arguments:
          updated_min: if different from None, only contacts that have been
                       updated from that date will be fetched. This format of
                       updated_min is a date string like this:
                       2010-09-12T17:23:01Z
        """
        contacts = []
        contacts_seen = 0
        page, total_contacts = self.fetch_contacts(contacts_seen + 1,
                                                   updated_min)
        contacts.extend(page)
        contacts_seen += len(page)

        while contacts_seen < total_contacts:
            page, total_contacts = self.fetch_contacts(contacts_seen + 1,
                                                       updated_min)
            contacts.extend(page)
            contacts_seen += len(page)

        return contacts

    def fetch_contacts(self, start_index, updated_min):
        """Aux method for sync. It fetches one page of contacts.

        Arguments:
          start_index: 1-based index of the first contact to fetch.
          updated_min: see the updated_min argument of the sync method.
        """
        if self.verbose:
            print 'Fetching contacts starting at', start_index

        query = gdata.contacts.client.ContactsQuery(
            updated_min=updated_min,
            start_index=start_index,
            orderby='lastmodified',
            sortorder='descending',
            )

        contacts_feed = self.client.get_contacts(query=query)
        contacts = [contact2dict(contact,
                                 self.singlevalue_attributes,
                                 self.multivalue_attributes)
                    for contact in contacts_feed.entry]
        return contacts, int(contacts_feed.total_results.text)


def safe_match(needle, haystack):
    """Utility function for comparing two values.

    Arguments:
      needle: string to compare.
      haystack: string or list of strings to look into.
    """

    def list_cmp():
        """Internal function used when haystack is a list"""
        for item in haystack:
            if needle.lower() in item.lower():
                return True
        else:
            return False

    def string_cmp():
        """Internal function used when haystack is a string"""
        return needle.lower() in haystack.lower()

    return list_cmp() if isinstance(haystack, list) else string_cmp()


class AddressBook(dict):
    """Address Book implementation using plain files.

    The contacts are stored in a text file using the json format.

    Each contact must have an unique 'id' attribute. All the other
    attributes are optional.
    """

    def __init__(self, filename, *args, **kwargs):
        """Constructor.

        Arguments:
          filename: where to load/save the contacts
        """
        super(AddressBook, self).__init__(*args, **kwargs)
        self.filename = filename

    def add_or_update_contact(self, contact):
        """Adds or updates a contact.

        If the contact is present in the address book it is updated. Otherwise
        it is added. Remember to call the load method before adding contacts
        or the new contacts will be replaced with the old ones.

        Arguments:
          contact: dictionary with the contact data
        """
        contact_id = contact['id']
        old_data = {}
        if contact_id in self:
            old_data = self[contact_id]
        old_data.update(contact)
        self[contact_id] = old_data

    def load(self):
        """Loads the contents of the file that stores the contacts"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as filedesc:
                for contact in json.load(filedesc):
                    self.add_or_update_contact(contact)

    def save(self):
        """Saves the contacts into the file that stores the contacts"""
        with open(self.filename, 'w') as filedesc:
            json.dump(self.values(), filedesc)

    def last_modified(self):
        """Return the date of the last modification to the file
        that stores the contacts in the format "%Y-%m-%dT%H:%M:%SZ"
        """
        if os.path.exists(self.filename):
            mtime = os.path.getmtime(self.filename)
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))

    def query(self, *args):
        """Perform a query in the contact set.

        Each arg defines a criteria. The query returns contacts
        that matches any of the criteria args.
        """
        for criteria in args:
            for contact in self.find_contact(criteria):
                yield contact

    def find_contact(self, criteria):
        """Find a contact that maches a criteria.

        Arguments:
          criteria: a string with two parts separated by a : characcter.
                    The first part is the attribute in where to look for a
                    match. The second part is the value to match.

                    If no ':' is found in the criteria, all attributes
                    will be matched except the 'id' attribute.
        """
        if ':' in criteria:
            attr, query_value = criteria.split(':')
        else:
            attr = None
            query_value = criteria

        for contact in self.values():
            if attr is None:
                for key, value in contact.items():
                    if key == 'id':
                        continue
                    if safe_match(query_value, value):
                        yield contact

            else:
                if attr not in contact:
                    continue

                value = contact[attr]
                if safe_match(query_value, value):
                    yield contact


def get_contact_entry_value(contact, accessor):
    """Returns one value of a contact entry

    Arguments:
      contact: the contact entry feed. See GData documentation.
      accessor: string with the attribute chain to get to the value.
                Example: name.text
    """
    value = contact
    for part in accessor.split('.'):
        value = getattr(value, part)
        if value is None:
            break
    return value


def contact2dict(contact, singlevalue_attributes, multivalue_attributes):
    """Converts a contact entry feed into a dictionary.

    Arguments:
      contact: the contact entry feed. See GData documentation
      singlevalue_attributes:
      multivalue_attributes:
    """
    result = {'id': contact.id.text}

    for attr, accessor in singlevalue_attributes:
        value = get_contact_entry_value(contact, attr + '.' + accessor)
        if value is not None:
            result[attr] = value

    for attr, accessor in multivalue_attributes:
        value_list = getattr(contact, attr)
        if len(value_list) > 0:
            result[attr] = [get_contact_entry_value(value, accessor)
                            for value in value_list]
    return result


# Registry for output functions
OUTPUT_REGISTRY = {}


def register_output_printer(name):
    """Decorator for output functions.

    Arguments:
      name: identifier for the output function
    """

    def inner_decorator(fnc):
        """This is the real decorator that register the function
        into the registry dictionary.

        Arguments:
          fnc: function to register
        """
        OUTPUT_REGISTRY[name] = fnc
        return fnc

    return inner_decorator


@register_output_printer('simple')
def simple_printer(contacts, codec='utf8'):
    """Print contacts showing the id and the updated attributes
    and then all the available attributes.
    """
    lines = []
    for contact in contacts:
        lines.append(u'id: %s' % contact['id'])
        for key, value in contact.items():
            if key in ('id', 'updated'):
                continue
            if isinstance(value, list):
                value = u', '.join(value)
            lines.append(u'\t%s: %s' % (key, value))
        if 'updated' in contact:
            lines.append(u'\tupdated: %s' % contact['updated'])
    lines = u'\n'.join(lines)
    print lines.encode(codec)


@register_output_printer('json')
def json_printer(contacts, codec='utf8'):
    """Print contacts in json format"""
    print json.dumps(tuple(contacts)).encode(codec)


@register_output_printer('mutt')
def mutt_printer(contacts, codec='utf8'):
    """Print contacts in a mutt friendly way"""
    lines = []
    for contact in contacts:
        for email in contact.get('email', []):
            title = contact.get('title', u'Unknown')
            other = contact.get('nickname', u'')
            lines.append(u'%s\t%s\t%s' % (email, title, other))
    lines = u'\n'.join(lines)
    print lines.encode(codec)


def abort(msg):
    """Utility function that exits the program with a message"""
    print >> sys.stderr, msg
    sys.exit(1)


def main():
    """Program entry point"""
    parser = optparse.OptionParser(usage="usage: %prog [options] queryargs",
                                   version=__version__)
    parser.add_option("-u", "--user", dest="user", default=None,
                      help="Google account email")
    parser.add_option("-p", "--password", dest="password", default=None,
                      help="Google account password")
    parser.add_option("-s", "--store", dest="store", default='contacts.data',
                      help="Where to save the contacts")
    parser.add_option("-v", "--verbose", action='store_true', dest="verbose",
                      default=False, help="Print verbose output")
    parser.add_option("-o", "--output-type", dest="output_type", type='choice',
                      choices=OUTPUT_REGISTRY.keys(), default='simple',
                      help="Type of output to print")
    parser.add_option("-c", "--codec", dest="codec", default="utf8",
                      help="Codec to use when printing results")
    (options, args) = parser.parse_args()

    output_printer = OUTPUT_REGISTRY.get(options.output_type, None)
    if output_printer is None:
        abort('The output type "%s" is not supported' % options.output_type)

    if options.user is None:
        abort('The user argument is mandatory')

    address_book = AddressBook(options.store)
    address_book.load()
    try:
        contacts = ContactsImporter(options.user, options.password,
                                    options.verbose)
        contacts = contacts.sync(address_book.last_modified())
    except gdata.client.RequestError:
        contacts = []
        if options.verbose:
            print >> sys.stderr, 'Error contacting Google Servers'

    for contact in contacts:
        address_book.add_or_update_contact(contact)
    address_book.save()
    output_printer(address_book.query(*args), options.codec)

if __name__ == '__main__':
    main()
