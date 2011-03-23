from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery

datatables_lib = Library('datatables', 'datatables-build')

datatables = ResourceInclusion(
    datatables_lib, 'media/js/jquery.dataTables.js',
    depends=[jquery],
    minified='media/js/jquery.dataTables.min.js')
