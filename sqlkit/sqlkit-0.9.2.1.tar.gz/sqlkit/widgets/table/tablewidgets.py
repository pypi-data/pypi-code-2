from sqlkit.widgets.common.completion import SimpleCompletion, FkeyCompletion, M2mCompletion
from sqlkit import _

class CellWidget(object):

    def __init__(self, field):
        self.field = field
        self.master = master = field.master
        self.field_name = field_name = field.field_name
        

        self.add_completion()

        self.master.field_widgets[field_name] = self
        
    def set_not_null_style(self):
        # FIXME: should set label in bold italics...
        pass

    def get_entry(self):
        # CellWidget has an editable only if we're editing...
        if self.field_name == self.master.currently_edited_field_name:
            return self.master.cell_entry.entry
        else:
            msg = _("No current obj for field '%s' in %s")
            raise NotImplementedError(msg  % (self.field_name, self.master))
    
    entry = property(get_entry)

    def add_completion(self, editable=False):
        """completion is set just for fkey and string fields"""

        
        if self.master.relationship_mode == 'm2m' and editable == False:
            Completion = M2mCompletion
            
        elif self.master.is_fkey(self.field_name):
            Completion = FkeyCompletion

        elif self.master.get_field_type(self.field_name) in (str, unicode):
            Completion = SimpleCompletion
        else:
            self.completion = None
            return
        
        self.completion = Completion(self.master, self, self.field_name)
        self.master.completions[self.field_name] = self.completion
        
    def set_value(self, value, shown=False):
        self.master.set_value(self.field_name, value, shown=shown)

    def get_value(self, shown=False):
        return self.master.get_value(self.field_name)

    def set_max_length(self, length=None):
        if length is None:
            length = self.field.length
            
        try:
            self.entry.set_max_length(length)
        except:
            pass
            
    def __str__(self):
        return "<CellWidget: %s>" % self.field_name 
