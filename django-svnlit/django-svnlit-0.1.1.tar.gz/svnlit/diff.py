import re
import difflib


DIFF_OPTCODE_MAP = {' ': 'nil', '-': 'sub', '+': 'add', '^': 'chg'}


def optcodes_to_slices(optcodes):
    if optcodes.startswith('? '):
        optcodes = optcodes[2:-1]
    sections = filter(lambda x: x, re.split('( +)', optcodes))
    slices = []
    for x in range(len(sections)):
        start_pos = reduce(lambda x, y: x + len(y), sections[:x], 0)
        end_pos = start_pos + len(sections[x])
        slices.append((slice(start_pos, end_pos), sections[x][0]))
    slices.append((slice(len(optcodes), None), ' '))
    return slices


def diff(content_from, content_to):
    diff_lines = list(difflib.Differ().compare(
        content_from.splitlines(), content_to.splitlines()))

    data_lines = []
    line_no = 0
    line_padding = len(str(len(diff_lines)))
    line_no_a = line_no_b = 0

    for line in diff_lines:
        if line.startswith('? '):
            slices = optcodes_to_slices(line)
            spans = map(lambda x: {
                'type': DIFF_OPTCODE_MAP[x[1]],
                'text': data_lines[-1]['slices'][0]['text'][x[0]]}, slices)
            line = {
                'type': DIFF_OPTCODE_MAP['^'], 'slices': spans,
                'number_a': data_lines[-1]['number_a'],
                'number_b': data_lines[-1]['number_b']}
            data_lines[-1] = line
            if data_lines[-2]['type'] != DIFF_OPTCODE_MAP[' ']:
                data_lines[-2]['type'] = DIFF_OPTCODE_MAP['^']

        else:
            if line[:1] == '+':
                line_no_a += 1; number_a = line_no_a; number_b = ''
            elif line[:1] == '-':
                line_no_b += 1; number_a = ''; number_b = line_no_b
            elif line[:1] == ' ':
                line_no_a += 1; line_no_b += 1
                number_a = line_no_a; number_b = line_no_b
            data_lines.append({
                'type': DIFF_OPTCODE_MAP[line[:1]],
                'number_a': unicode(number_a).rjust(line_padding),
                'number_b': unicode(number_b).rjust(line_padding),
                'slices': [{'type': DIFF_OPTCODE_MAP[' '], 'text': line[2:]}]})

        line_no += 1

    return data_lines
