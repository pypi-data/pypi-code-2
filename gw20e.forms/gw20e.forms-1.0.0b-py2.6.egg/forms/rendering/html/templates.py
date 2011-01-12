CONTROL_HDR="""<div id="%(id)s" class="control %(type)s %(extra_classes)s">
<label for="input-%(id)s">%(label)s</label>
<div class="alert"></div>
<div class="hint">%(hint)s</div>"""
CONTROL_HDR_PLAIN="""<div id="%(id)s" class="control %(type)s %(extra_classes)s">"""
CONTROL_FTR="""</div>"""

CARDGROUP_TPL_HDR = """<fieldset id="%(id)s" class="cards %(extra_classes)s">
<legend>%(label)s</legend>"""
CARDGROUP_TPL_FTR="""</fieldset>"""

STEPGROUP_TPL_HDR = """<fieldset id="%(id)s" class="steps %(extra_classes)s">
<legend>%(label)s</legend>"""
STEPGROUP_TPL_FTR="""</fieldset>"""
STEPGROUP_NAV_PREV="""<li class="stepsnav previous disabled">
</li>"""
STEPGROUP_NAV_NEXT="""<li class="stepsnav next">
</li>"""
STEPGROUP_NAV_SAVE="""<li class="stepsnav save">
<input type="submit" value=""/>
</li>"""

FLOWGROUP_TPL_HDR = """<fieldset id="%(id)s"
  class="flow %(orientation)s %(extra_classes)s">
<legend>%(label)s</legend>"""
FLOWGROUP_TPL_FTR="""</fieldset>"""

INPUT_TPL = """<input id="input-%(id)s" type="text"
  name="%(id)s" value="%(value)s"/>"""

INPUT_LARGE_TPL = """<textarea id="input-%(id)s"
  name="%(id)s">%(value)s</textarea>"""

TEXT_TPL = """<p class="text" id="%(id)s">%(text)s</p>"""

SELECT_ALL_HDR_TPL = """"""
SELECT_ALL_FTR_TPL = """<input class="all" type="checkbox"
name="all_%(id)s"/><label class="after">Alles</label><br/>"""

CHECK_TPL = """<input type="checkbox" id="input-%(value)s" value="%(value)s"
  %(checked)s
  name="%(id)s"/><label class="after"
  for="input-%(value)s">%(label)s</label><br/>"""

RADIO_TPL = """<input type="radio" id="input-%(value)s" value="%(value)s"
  %(checked)s
  name="%(id)s"/><label class="after"
  for="input-%(value)s">%(label)s</label><br/>"""  

OPTION_TPL = """<option value="%(value)s" %(selected)s>%(label)s</option>"""

COLORPICKER_TPL = """<input id="input-%(id)s" type="text"
  name="%(id)s" value="%(value)s"/><div class="colorpicker"></div>"""

SUBMIT_TPL = """<input type="submit" id="%(id)s" value="%(label)s"/>"""

RICHTEXT_TPL = """<textarea id="input-%(id)s"
  cols="80"
  rows="25"
  class="mce_editable"
  title='%(richconfig)s'
name="%(id)s">%(value)s</textarea>
<script type="text/javascript">
  tinymce.dom.Event.add(window,
                        'load',
                        function(e) {
                          var config = new TinyMCEConfig('input-%(id)s');
                          config.init();
                        });
</script>
"""
