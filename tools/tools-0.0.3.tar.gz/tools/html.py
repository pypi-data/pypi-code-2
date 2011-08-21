from htmlentitydefs import name2codepoint
import re

def convert_entities(text):
    """
    Convert HTML entities to their unicode analogs.
    """

    re_entity = re.compile(r'(&[a-z]+;)')
    re_num_entity = re.compile(r'(&#\d+;)')

    def process_entity(match):
        entity = match.group(1)
        name = entity[1:-1]
        if name in name2codepoint:
            return unichr(name2codepoint[name])
        else:
            return entity

    
    def process_num_entity(match):
        entity = match.group(1)
        num = entity[2:-1]
        try:
            return unichr(int(num))
        except ValueError:
            return entity

    text = re_num_entity.sub(process_num_entity, text)
    text = re_entity.sub(process_entity, text)
    return text


def escape(text):
    """
    Returns the given HTML with ampersands, quotes and angle brackets encoded.
    """

    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
