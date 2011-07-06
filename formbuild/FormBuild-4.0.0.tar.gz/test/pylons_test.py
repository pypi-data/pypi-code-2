from webhelpers.html import literal
import sys; sys.path.append('../')
from formbuild import Form
         
class LiteralForm(Form):
    def __getattribute__(self, name):
        if name in [
            'value',
            'option',
            'error',
            'checked',
            'table_class',
            'end',
        ]:
            return Form.__getattribute__(self, name)
        def make_literal(*k, **p):
            return literal(getattr(Form, name)(self, *k, **p))
        return make_literal

form = LiteralForm(
    value = {
        'file':''
    },
    error= {
        'file_upload':u'Please select a file for processing.'
    }
)
lines = [
    form.start_with_layout(
        '/some/url',
        table_class='upload_form',
    ),
    form.row('<h2>Upload file for processing</h2>'),
    form.field(
        label="File",
        type='file',
        name='file'
    ),
    form.action_bar(
        form.submit(name='action', value='Submit')
    ),
    form.end_with_layout(),
]

assert '\n'.join(lines) == """\
<form action="/some/url" method="post"><table class="upload_form">
<tr><td colspan="3"><h2>Upload file for processing</h2></td></tr>
<tr class="field">
  <td class="label" valign="top" height="10">
    <span style="visibility: hidden">*</span><label for="file">File:</label>
  </td>
  <td class="field" valign="top">
    <input type="file" name="file" />
  </td>
  <td rowspan="2" valign="top"></td>
</tr>
<tr>
  <td></td>
  <td colspan="2">
    <input type="submit" name="action" value="Submit" />
  </td>
</tr>
</table></form>"""

print "Test passed."

