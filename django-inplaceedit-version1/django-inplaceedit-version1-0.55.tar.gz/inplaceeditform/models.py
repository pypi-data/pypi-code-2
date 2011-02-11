class InplaceEditModel(object):

    def can_edit_this_object(self, user):
        return False
    
    @property
    def text_empty_value(self):
        return ''
    
    @property
    def can_be_value_none(self):
        return True
