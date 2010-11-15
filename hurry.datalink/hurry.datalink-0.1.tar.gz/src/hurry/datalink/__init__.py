from hurry.resource import Library, ResourceInclusion

datalink_lib = Library('datalink_lib', 'datalink-build')

datalink = ResourceInclusion(datalink_lib, 'jquery.datalink.js')
#                minified='datalink.min.js')
