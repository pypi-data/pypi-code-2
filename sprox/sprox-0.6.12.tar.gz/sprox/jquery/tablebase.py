from sprox.tablebase import TableBase
from sprox.metadata import FieldsMetadata

from tw.jquery import FlexiGrid

class JQueryTableBase(TableBase):
    """This class allows you to credate a table widget.

    :Modifiers:
    +-----------------------------------+--------------------------------------------+------------------------------+
    | Name                              | Description                                | Default                      |
    +===================================+============================================+==============================+
    | __url__                           | url that points to the method for data     | None                         |
    |                                   | filler for this table                      |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+

    also see modifiers in :mod:`sprox.tablebase`

    """

    #object overrides
    __base_widget_type__=FlexiGrid
    __url__ = None

    def _do_get_widget_args(self):
        #args = super(DojoTableBase, self)._do_get_widget_args()
        columns = []
        for field in self.__fields__:
            columns.append(dict(name=field, display=self.__headers__.get(field, field), width=80))
        identifier = self.__provider__.get_primary_field(self.__entity__)

        args = dict(id=self.__entity__.__name__+'_table',
                    fetchURL=self.__url__,
                    title=self.__entity__.__name__,
                    colModel=columns,
                    useRp=True,
                    rp=25,
#                    sortname=identifier,
#                    sortorder='asc',
                    usepager=True,
#                    searchitems=searchitems,
                    showTableToggleButton=True,
                    #buttons=buttons,
                    #width=500,
                    #height=200
                    )
        return args