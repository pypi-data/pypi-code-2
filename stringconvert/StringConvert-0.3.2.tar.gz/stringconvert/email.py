"""\
Email converter, desgined to be compatible with FormEncode
"""

import re
import socket

# Use ConversionKit internationalisation tools
from conversionkit import message, _
from conversionkit.exception import ConversionError
from stringconvert import StringConvertError
from bn import AttributeDict

try:
    import DNS
    DNS.DiscoverNameServers()
    have_dns=True
except ImportError:
    have_dns=False

try:
    import nestedrecord
    have_nestedrecord = True
except ImportError:
    have_nestedrecord = True

usernameRE = re.compile(r"^[^ \t\n\r@<>()]+$", re.I)
domainRE = re.compile(r'''
    ^(?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                       # TLD
''', re.I | re.VERBOSE)

def unicodeToEmail(
    resolve_domain=False, 
    strip=True,
    msg_no_at           = _(u'An email address must contain a @ character'),
    msg_multiple_at     = _(u'An email address must contain only one @ character'),
    msg_bad_username    = _(u'The username portion of the email address is invalid (the portion before the @: %(username)s)'),
    msg_socket          = _(u'Could not connect to the server for that email, please choose a valid email'),
    msg_bad_domain      = _(u'The domain portion of the email address is invalid (the portion after the @: %(domain)s)'),
    msg_no_such_domain  = _(u'The domain of the email address does not exist (the portion after the @: %(domain)s)'),
):
    """
    Convert an email address.

    If you pass ``resolve_domain=True``, then it will try to resolve the domain
    name to make sure it's valid.  This takes longer though.  You must have the
    `PyDNS <http://pydns.sf.net>`_ modules installed to look up DNS (MX and A)
    records.
   
    On Debian-based systems you can install it like this::

        $ sudo apt-get install python-dns

    on others::

        $ easy_install pydns

    """
    # Could not reproduce the API for these two tests:
    # >>> e = Email(not_empty=False)
    # >>> e.to_python('')
    if resolve_domain:
        if not have_dns:
            import warnings
            warnings.warn(
                "PyDNS <http://pydns.sf.net> is not installed on your system "
                "(or the DNS package cannot be found). Domain names in "
                "addresses cannot be resolved."
            )
            raise ImportError("No module named DNS, have you installed pydns?")

    def unicodeToEmail_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            raise StringConvertError(
                'The value %r is not a Unicode object'%conversion.value
            )
        if strip:
            result = conversion.value.strip()
        else:
            result = conversion.value
        # The DNS code can't deal with unicode, so we'll use ascii until the 
        # end, then convert to unicode
        result = str(result)
        if not result.strip():
            conversion.result = ''
            return 
        elif not '@' in result: 
            conversion.error = message(state, msg_no_at)
        elif result.count('@') != 1:
            conversion.error = message(state, msg_multiple_at)
        else:
            username, domain = result.split('@')
            if not usernameRE.search(username):
                conversion.error = message(
                    state, 
                    msg_bad_username,
                    dict(username=username)
                )
            elif not domainRE.search(domain):
                conversion.error = message(
                    state, 
                    msg_bad_domain, 
                    dict(domain=domain)
                )
            else:
                if resolve_domain:
                    assert have_dns, "pyDNS should be available"
                    try:
                        a=DNS.DnsRequest(domain, qtype='mx', timeout=3).req().answers
                        if not a:
                            a=DNS.DnsRequest(domain, qtype='a', timeout=3).req().answers
                        dnsdomains=[x['data'] for x in a]
                    except (socket.error, DNS.DNSError), e:
                        conversion.error = message(
                            state, 
                            msg_socket, 
                            dict(error=e)
                        )
                    else:
                        if not dnsdomains:
                            conversion.error = message(
                                state,
                                msg_no_such_domain,
                                dict(domain=domain)
                            )
                        else:
                            conversion.result = unicode(result)
                else:
                    conversion.result = unicode(result)
    return unicodeToEmail_converter

def just_alpha(input):
    output = []
    input = input.lower()
    for char in input:
        if ord(char)>=97 and ord(char)<=122:
            output.append(char)
    return ''.join(output)

def parse_name(name, i):
    parts = name.split(' ')
    if len(parts):
        # We might have a first name and a surname
        if parts[0].lower() in ['mr', 'mrs', 'dr']:
            parts = parts[1:]
        if len(parts) == 1:
            return {'firstname': name.capitalize(), 'middlenames': u'', 'lastname': u''}
        else:
            return {
                'firstname': parts[0].capitalize(),
                'middlenames': u' '.join(parts[1:-1]),
                'lastname': parts[-1].capitalize(),
            }
    else:
        return {'firstname': name, 'middlenames': u'', 'lastname': u''}

def parse_organisation(domain):
    result = {'organisation': u''}
    if domain:
        result['organisation'] = domain.split('.')[0].capitalize()
    return result

def parse_invite(invite, split_name=False, extract_organisation=False):
    """\
    """
    if not isinstance(invite, unicode):
        raise StringConvertError(
            'Expected a unicode string, not %r'%type(invite)
        )
    invite = invite.replace(',', '\r').replace('\r', '\n').replace('\n', ';')
    invites = invite.split(';')
    final = []
    i=0
    for string in invites:
        string = string.strip()
        if not string:
            continue
        if '@' in string:
            parts = string.split('@')
            if not parts:
                # Assume we have a name
                raise ConversionError('No email assoicated with the name for item %s in the list of emails'%i)
            elif len(parts) > 2:
                raise ConversionError("Did not expect two '@' characters in item %s in the list of emails"%i)
            else:
                result = {'email':u''}
                domain = parts[-1]
                if extract_organisation:
                    result.update(parse_organisation(domain))
                name_and_email = parts[-2].strip()
                parts = name_and_email.split('<')
                email = parts[-1].strip()+'@'+domain
                email = email.strip('<>')
                result['email'] = email
                if not parts[:-1]:
                    # Let's just use the first part of the email address
                    name = name_and_email.replace('.', ' ')
                else:
                    name = '<'.join(parts[:-1]).strip()
                if split_name:
                    result.update(parse_name(name, i))
                else:
                    result['name'] = name
                final.append(AttributeDict(result))
        else:
            final.append(AttributeDict(parse_name(string, i)))
        i+=1
    return final

def listOfEmails(split_name=False, extract_organisation=False):
    if not have_nestedrecord:
        import warnings
        warnings.warn(
            "The NestedRecord package is not installed on your system so"
            "listOfEmails() cannot be used."
        )
        raise ImportError("No module named 'nestedrecord'")

    def listOfEmails_converter(conversion, state=None):
        try:
            conversion.result = parse_invite(
                conversion.value, 
                split_name=split_name,
                extract_organisation=extract_organisation,
            )
        except ConversionError, e:
            conversion.error = str(e)
        except:
            conversion.error = 'Could not parse the list of email addresses, please check the syntax'
            raise
    return listOfEmails_converter


