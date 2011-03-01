from xml.etree.ElementTree import Element, tostring
elem = Element("{http://schemas.openxmlformats.org/package/2006/content-types}")
print(tostring(elem))
