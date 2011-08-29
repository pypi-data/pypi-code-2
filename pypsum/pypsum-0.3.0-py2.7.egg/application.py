from flask import Flask, request, abort, url_for
from flask import json, make_response, render_template
from flask import __version__ as flask_version
from loremipsum import __version__ as loremipsum_version
from copy import deepcopy
from string import strip
from cgi import parse_header
import time
import os
import sys
import settings
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                import cElementTree as etree
            except ImportError:
                import elementtree.ElementTree as etree


# Application setup
pypsum = Flask(settings.NAME)
pypsum.config.from_object(settings)
_settings = os.environ.get('%s_SETTINGS' % settings.NAME.upper(), '').strip()
if os.path.isfile(_settings):
    application.config.from_pyfile(_settings)
elif _settings:
    application.config.from_object(_settings)

# Skeleton state object.
_state = {
    'loremipsum': {
        'header': {
            'generation_time': 0,
            'words': 0,
            'sentences': 0,
            'paragraphs': 0,
        },
        'body': [
        ]
    }
}

def xml_representation(state, *args):
    """
    Builds an xml representation of the state.

    :param state: the built state
    :type state: dict
    :returns: the xml representation of the state
    :rtype: str
    """
    xml = etree.Element('loremipsum')
    header = etree.Element('header')
    body = etree.Element('body')
    for label in ['words', 'sentences', 'paragraphs', 'generation_time']:
        tag = etree.Element(label)
        tag.text = str(state['loremipsum']['header'][label])
        header.append(tag)
    xml.append(header)
    for item in state['loremipsum']['body']:
        label, text = item.popitem()
        tag = etree.Element(label)
        tag.text = text
        body.append(tag)
    xml.append(body)

    return etree.tostring(xml)

def json_representation(state, *args):
    """
    Builds an json representation of the state.

    :param state: the built state
    :type state: dict
    :returns: the json representation of the state
    :rtype: str
    """
    representation = json.dumps(state, indent=None if request.is_xhr else 2)
    # JASONP support
    callback = request.args.get('callback','')
    if callback:
        return 'callback(%s)' % representation
    return representation

def html_representation(state, amount, text_start, text_type, link):
    """
    Builds an html representation of the state.

    :param state: the built state.
    :type state: dict
    :returns: the html representation of the state
    :rtype: str
    """
    return render_template('state.html',
        state=state, amount=amount, text_start=text_start, text_type=text_type, next=link)

def content_type_representation():
    available = {
        'text/html': html_representation,
        'application/xml': xml_representation,
        'application/json': json_representation
    }
    accepted = map(parse_header, request.headers['Accept'].split(','))
    for content_type, parameters in accepted:
        representation = available.get(content_type, None)
        if representation:
            return (content_type, representation)
    # The requested resource is only capable of generating content not
    # acceptable according to the Accept headers sent in the request.
    abort(406)

@pypsum.route('/')
def index():
    """
    Returns the application front page.
    """
    return make_response(render_template('index.html'))

@pypsum.route("/generate/<int:amount>/<any('lipsum','setiam'):text_start>/<any('sentences', 'paragraphs'):text_type>")
def generate(amount, text_start, text_type):
    """
    The application core function. Based on the Accept header, chooses the
    representation of the state, builds the state object using the loremipsum
    module, and then returns the response.

    :param amount: the amount of text to produce
    :type amount: int
    :param text_start: if text should satrt with standard "Lorem ipsum" or not
    :type amount: any('lipsum', 'setiam')
    :param text_type: if text shoul be paragraph or a simple sentence.
    :type text_type: any('sentences', 'paragraphs')
    """
    return _generate(amount, text_start, text_type)

@pypsum.route("/generator")
def generator():
    amount = request.args.get('amount', None)
    text_start = request.args.get('text_start', None)
    text_type = request.args.get('text_type', None)
    if all([amount, text_type, text_start]):
        return _generate(int(amount), text_start, text_type)
    # The request cannot be fulfilled due to bad syntax.
    abort(400)

def _generate(amount, text_start, text_type):
    """
    Real content generator.
    """
    content_type, representation = content_type_representation()

    # Eventually generate url for next page of content.
    capacity = {
        'words': pypsum.config['WORDS_CAPACITY'],
        'sentences': pypsum.config['SENTENCES_CAPACITY'],
        'paragraphs': pypsum.config['PARAGRAPHS_CAPACITY']}.get(text_type)
    link = ''
    if amount > capacity:
        link = url_for(request.endpoint,
            amount=amount-capacity, text_start='setiam', text_type=text_type)
        amount = capacity

    # Text generatin setup. Remove trailing "s" from label.
    sentences, words, body, label = 0, 0, [], text_type[:-1]
    generate = getattr(pypsum.config['GENERATOR'], 'generate_' + text_type)

    # Generate content.
    generation_start = time.time()
    generated = generate(amount, (text_start == 'lipsum'))
    for generated_sentences, generated_words, text in generated:
        body.append({label: text})
        words += generated_words
        sentences += generated_sentences
    state = deepcopy(_state)
    state['loremipsum']['header']['words'] = words
    state['loremipsum']['header']['sentences'] = sentences
    if text_type == 'paragraphs':
        state['loremipsum']['header']['paragraphs'] = amount
    state['loremipsum']['body'] = body
    generation_time = time.time() - generation_start
    state['loremipsum']['header']['generation_time'] = generation_time

    # Build response.
    response = make_response(
            representation(state, amount, text_start, text_type, link))
    response.headers['Content-Type'] = content_type
    response.headers['Link'] = '<%s>; rel="next"' % link
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Powered-By'] = 'Flask/%s, loremipsum/%s' % (
            flask_version, loremipsum_version)
    response.headers['X-Runtime'] = '%s.%s.%s-%s%s' % tuple(sys.version_info)
    return response

