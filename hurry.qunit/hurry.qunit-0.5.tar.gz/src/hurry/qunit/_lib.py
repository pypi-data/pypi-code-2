from hurry.resource import Library, ResourceInclusion

qunit_lib = Library('qunit_lib', 'qunit-build')

css = ResourceInclusion(qunit_lib, 'qunit.css')
qunit = ResourceInclusion(qunit_lib, 'qunit.js', depends=[css])
