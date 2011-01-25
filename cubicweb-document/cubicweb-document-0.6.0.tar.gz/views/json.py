# tabs, diffs, treestate ########################################################################
from logilab.common.decorators import monkeypatch
from cubicweb.web.views.basecontrollers import JSonController

@monkeypatch(JSonController)
def js_update_edition_status(self, vfrql, usereid, will_edit):
    vf = self._cw.execute(vfrql).get_entity(0, 0)
    if will_edit:
        vf.mark_downloaded_for_edition_by(usereid)
    else:
        vf.unmark_user_for_edition(usereid)

