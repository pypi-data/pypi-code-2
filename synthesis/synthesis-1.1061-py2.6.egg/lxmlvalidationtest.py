from lxml import etree

schema_file_location = '/home/user/workspace/synthesis/installer/build/xsd/versions/HMISXML/28/HUD_HMIS.xsd'
instance_file_location = '/home/user/workspace/synthesis/TestFiles/Example_HUD_HMIS_2_8_Instance.xml'

schemafileobject = open(schema_file_location,'r')
instancefileobject = open(instance_file_location,'r')

etreeinstanceobject = etree.parse(instancefileobject)
etreeschemaobject = etree.parse(schemafileobject)

xmlschema = etree.XMLSchema(etreeschemaobject)
if xmlschema.validate(etreeinstanceobject):
    print "Validates"
else:
    print "Doesn't validate"
