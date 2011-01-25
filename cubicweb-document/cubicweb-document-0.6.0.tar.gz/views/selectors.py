from cubicweb.selectors import match_search_state, lltrace

class mimetype(match_search_state):
    @lltrace
    def __call__(self, cls, req, rset, **kwargs):
        doc = rset.get_entity(0, 0)
        if hasattr(doc, 'branch_head'):
            doc = doc.branch_head()
        if hasattr(doc, 'data_format'):
            format = doc.data_format
        else:
            format = 'application/octet-stream'
        return format in self.expected
