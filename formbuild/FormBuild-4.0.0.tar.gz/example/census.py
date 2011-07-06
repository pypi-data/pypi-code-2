"""\
ConversionKit and FormBuild example

Usage (from the same directory as this file), there should be no difference
produced by ``diff``:

    wget http://pylonsbook.com/virtualenv.py
    python virtualenv.py env
    env/bin/easy_install formconvert formbuild
    env/bin/python 03_conversionkit.py > output.txt
    diff expected_output.txt output.txt

Background:

    FormBuild and FormConvert are only designed to work with data that
    fits a data model I call the "Nested list Of Records Model" (NORM). That 
    data model supports only these things:
    
    * dictionaries called *records* where the keys are valid Python, JavaScript and
      SQL identifiers and the values are either unicode strings or lists of records
    
    * where a value is a list of records, all the records must be of the same type
      and structure.
    
    This means that lists of unicode strings, dictionaries as values and any other
    sort of data structure is forbidden.
    
    For each data structure you want your application to be able to support you
    therefore write two converters: one converts from a UNR data
    structure to the data structure your application needs and the other converts
    back.
    
    Any time the data coming into the application isn't in UNR format you need to
    write a separate converter to put it into that form. In this way, your
    application is always dealing with a consistent and predictable data structure
    and all complications occur at the boundary between the different components.

    Any time I've skipped these explicit conversions, or tried to re-use converters
    because at the moment the same one can be used for two things, I've regretted it.

Applied to this example:

    In this example, the source data fails to be a valid UNR structure in two ways:
    
    * The ``interests`` item is a list of strings, not a list of records
    * The format of certain elements such as ``interests`` and ``census_date`` is
      not Unicode
    
    This means we can't just show the UNR->app->form and POST->UNR->app conversions
    but must also write a converter to get our source data in the right format.
    
    At first sight this seems like extra effort, but actually it deals with the 
    complexity of the source data at the point it enters the system, so that
    the main application code can be completely standard.

Please note:

    This isn't how you'd normally lay out a ConversionKit or FormBuild example,
    I've just written it this way to be consistent with the other examples. Also
    I wouldn't have chosen this nameing. Names in the converters would exactly 
    mirror those used in the table columns (eg census_name would be name,
    people would be person, interests to interest etc).

    Also, I haven't made any changes to demo any of this (that would be unfair!).

    Use of formbuild is completely decoupled from conversionkit (you could replace
    either with another library and it would still run).

    Finally, new converters are really easy to write in this model because
    there is no state associated with them and all the results and errors are
    plain Python objects, nothing fancy, no magic.
"""

from common import interest_choices, invalid_sample_data, valid_sample_data

from conversionkit import Conversion, toDictionary, toListOf, oneOf
from stringconvert import unicodeToUnicode, unicodeToDate, stringToUnicode, stringToUnicode, toUnicode
from stringconvert.email import unicodeToEmail

from nestedrecord import encode, encode_error, decode, refactorListOfStrings
from formconvert import multiDictToDict
from formbuild import Form # You could subclass form to customise rendering methods

from urllib import urlencode
from cgi import FieldStorage

def build_fake_cgi_fieldset(result):
    """\
    Set up a fake submitted data object as if it had been submitted back
   
    Note: FormConvert can also handle WebOb objects, we're just using cgi instead so there is one less dependency.
    """
    flat = encode(result)
    fake_environ = {'QUERY_STRING': urlencode(flat)}
    return FieldStorage(environ=fake_environ, keep_blank_values=True)

#
# Convert from source to UNR (converters all go in lib.py)
#

# All converters can be re-used, they hold no state. Since we use this one
# a lot, let's not re-create it each time.
unicode_to_unicode = unicodeToUnicode()

#from conversionkit import chainConverters, tryEach
#each = chainConverters(
#    tryEach([unicodeToUnicode(), stringToUnicode()]),
#    unicodeToDate(),
#)
#print Conversion('2011-10-10').perform(each).result
#print Conversion(u'2011-10-10').perform(each).result


# Get the options in the form we need:
unicode_interest_options = [unicode(interest[0]) for interest in interest_choices]

source_to_unr_people = toDictionary(
    converters = dict(
        name = unicode_to_unicode,
        interests = refactorListOfStrings(),
    )
)
source_to_unr_census = toDictionary(
    converters = dict(
        census_name = unicode_to_unicode,
        census_email = unicode_to_unicode,
        census_date = stringToUnicode(),
        census_type = unicode_to_unicode,
        people = toListOf(source_to_unr_people),
    ),
)

#
# Now convert from UNR to our internal data structure (this will also be used for form validation)
#

unr_to_interests = toDictionary(
    converters = dict(
        id=oneOf(unicode_interest_options),
    ),
)
unr_to_people = toDictionary(
    converters = dict(
        name = unicode_to_unicode,
        interests = toListOf(unr_to_interests),
    ),
    # Just an example of specifying error states not related to the conversion
    # of a child converter (other ways of specifying the same thing too, eg with Field())
    missing_or_empty_errors = dict(
        name = u'Please specify your name',
    ),
)
unr_to_census = toDictionary(
    converters = dict(
        census_name = unicode_to_unicode,
        census_email = unicodeToEmail(),
        census_date = unicodeToDate(),
        census_type = unicode_to_unicode,
        people = toListOf(unr_to_people),
    ),
)


#
# Finally, serialise from our internal data structure back to UNR (here we can
# get away with using to_unicode everywhere because it happens that Python's
# default string representation is the same as the UNR format.
#

interests_to_unr = toDictionary(
    converters = dict(
        id=oneOf(unicode_interest_options),
    ),
)
people_to_unr = toDictionary(
    converters = dict(
        name = unicode_to_unicode,
        interests = toListOf(interests_to_unr),
    ),
    # Just an example of specifying error states not related to the conversion
    # of a child converter (other ways of specifying the same thing too, eg with Field())
    missing_or_empty_errors = dict(
        name = u'Please specify your name',
    ),
)
census_to_unr = toDictionary(
    converters = dict(
        census_name = unicode_to_unicode,
        census_email = unicode_to_unicode,
        census_date = toUnicode(), # We might write an explicit data converter here, but str(date) happens to give the right format.
        census_type = unicode_to_unicode,
        people = toListOf(people_to_unr),
    ),
)

#
# Helpers for generating forms (this code goes in the template)
#

def render_table(form):
    """\
    This bit is usually in the Python template:
    The code here would be the same for error and success states, also 
    there is no option information or values in the rendering code.
    Everything can still be accessed and overridden by passing more arguments to 
    the methods so you can take control here when you need it but generally data is 
    in the controller, presentation in the template
    """
    yield form.fieldset_start('Core Census Info')
    yield form.field('census_name', type='text', label='Name')
    # Here we'll use the full ``form.field()`` functionality which can handle display of errors 
    yield form.field('census_date', type='text', label='Date', field_desc='yyyy-mm-dd') # there are arguments for any layout of comments around fields and labels too
    yield form.field('census_email', type='text', label='Email', required=True) # Here "required" is simply a display thing, doesn't affect validation
    yield form.field('census_type', type='text', label='Type')
    yield form.fieldset_start('People')
    for people_counter, people in enumerate(census['people']):
        yield form.fieldset_start('Person %s'%(people_counter+1))
        yield form.field('people[%s].name' % people_counter, type='text', label='Name')
        # We don't need to loop for the interests checkbox group because FormBuild
        # knows that checkbox groups are often used for this case, we just
        # use the args dict to pass the sub_name to the form.checkbox_group() function
        checkbox_field_name = 'people[%s].interests' % people_counter
        yield form.field(checkbox_field_name, 'checkbox_group', args=dict(sub_name='id'))
        yield form.fieldset_end()
    yield form.action_bar([form.submit('submit', 'Save')])
    yield form.fieldset_end()

def render_raw(form):
    """\
    You don't have to use the funny table code the above default Form
    generates. At any point you can drop to using plain HTML. Here's
    another rendering of some of the form data demonstrating this:
    """
    yield '<form>'
    if 'census_email' in form.error:
        yield form.error['census_email']
    yield 'Email: ' + form.text('census_email')
    # Or you can drop even further and get the values directly too to generate raw HTML
    # for the fields too if you want to take responsibility for encodigng values
    yield 'Name: <input name="census_name" value="' + form.value.get('census_name') + '" />'
    yield '</form>'

if __name__ == '__main__':

    print "Now cleaning up..."
    unr_census = []
    for census in [valid_sample_data, invalid_sample_data]:
        conversion = Conversion(census).perform(source_to_unr_census)
        if conversion.successful:
            result = conversion.result 
            print "Success. Plain Python dict, no magic: ", result
            unr_census.append(result)
        else:
            error = conversion.error
            print "Error. This is a single string summary of the problem: ", error
            print "Detailed error structure:", encode_error(conversion)
    
    print "\nNow validating..."
    valid_internal_census = []
    invalid_internal_error_conversion = []
    for census in unr_census:
        conversion = Conversion(census).perform(unr_to_census)
        if conversion.successful:
            result = conversion.result 
            print "Success. Plain Python dict, no magic: ", result
            valid_internal_census.append(result)
        else:
            error = conversion.error
            print "Error. This is a single string summary of the problem: ", error
            print "Detailed error structure:", encode_error(conversion)
            invalid_internal_error_conversion.append(conversion)
   
    # Get the valid application data and the valid UNR census data
    result = valid_internal_census[0]
    value = unr_census[0]

    print "\nNow flattening..."
    flat = encode(value)
    print "Flattened: ", flat
    
    # You can build a form with it like this:
    form = Form(flat, option={'people[*].interests': interest_choices})
    
    print "\nNow rendering two valid forms..."
    print ''.join(list(render_table(form)))
    print ''.join(list(render_raw(form)))
        
    print "\nNow demonstrating handling form submission..."
    cgi_fs = build_fake_cgi_fieldset(value)
    conversion = Conversion(cgi_fs).perform(multiDictToDict(encoding='utf8')) # Note the encoding is explicit.
    flattened = conversion.result
    data = decode(flattened)
    print "Decoded:", data
    print  Conversion(data).perform(unr_to_census).result == result # Will be True

    print "\nNow rendering a form with errors..."
    conversion = invalid_internal_error_conversion[0]
    value = conversion.value # The initial data that went into the conversion
    error = encode_error(conversion)
    form = Form(encode(value), option={'people[*].interests': interest_choices}, error=error)
    print ''.join(list(render_table(form)))

